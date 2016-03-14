
/**
 * @typedef {{pipe: number}}
 */
var StepParams;

/**
 * @typedef {{name: string, params: StepParams}}
 */
var Step;

/**
 * @typedef {{queue: Array<!Step>, current: ?Step, running: boolean}}
 */
var Scenario;

/**
 * @typedef {{}}
 */
var Module;

/**
 * @const {number}
 */
var STEP_HEIGHT_UNIT = 64;

/**
 * @const {number}
 */
var STEP_WIDTH_UNIT = 128;

/**
 * @type {!Object<string, !Module>}
 */
var moduleCache = {};

/**
 * No Operation Performed
 */
function nop() {}

/**
 * @param {!Step} step
 * @param {function(!Module)} callback
 */
function stepModule(step, callback) {
  var module = moduleCache[step.name];
  if (module === undefined) {
    d3.json('/api/help/'+step.name, function(error, module) {
      if (module !== null) {
        callback(moduleCache[step.name] = module);
      } else {
        console.error(error);
      }
    });
  } else {
    callback(module);
  }
}

/**
 * @param {!Scenario} scenario
 */
function initControls(scenario) {
  d3.select('.loop-action').on('click', function() {
    if (scenario.running) {
      scenario.running = false;
      d3.json('/api/stop', nop);
    } else {
      scenario.running = true;
      d3.json('/api/start', nop);
    }

    redrawHeader(scenario);
  });

  d3.select('.scenario').on('click', function() {
    var target = d3.select(d3.event.target);
    if (target.classed('step')) {
      scenario.current = target.datum();

      redrawCircuit(scenario);

      stepModule(scenario.current, function(module) {
        redrawMenu(module);
      });
    }
  });
}


/**
 * @param {!Module} module
 */
function redrawMenu(module) {

}

/**
 * @param {!Scenario} scenario
 */
function redrawHeader(scenario) {
  d3.select('.loop-action')
      .classed('btn-success', !scenario.running)
      .classed('btn-danger', scenario.running)
}

/**
 * @param {!Scenario} scenario
 */
function redrawCircuit(scenario) {
  var circuit = d3.select('.scenario')
      .selectAll('.step')
      .data(scenario.queue);

  circuit
      .enter()
      .append('div')
      .classed('step', true)
      .classed('well', true)
      .text(function (step) { return step.name })
      .style('top', function(step, i) { return i * STEP_HEIGHT_UNIT + 'px' })
      .style('left', function(step) { return (step.params.pipe - 1) * STEP_WIDTH_UNIT + 'px' })
      .style('width', STEP_WIDTH_UNIT + 'px')
      .style('height', STEP_HEIGHT_UNIT + 'px');

  circuit
      .classed('current', function(step) { return step === scenario.current; });
}


/**
 * @param {Error} error
 * @param {Scenario} scenario
 */
function init(error, scenario) {
  if (scenario !== null) {
    scenario.current = null;
    scenario.running = false;

    initControls(scenario);

    redrawHeader(scenario);
    redrawCircuit(scenario);
  } else {
    console.error(error);
  }
}

/**
 * Application bootstrap.
 */
function main() {
  d3.json('/api/get_conf', init);
}
