//Create a Pixi Application
let app = new PIXI.Application({
    antialias: true,
    transparent: false,
    resolution: 1,
    width: 840,
    height: 820,
  }
);

app.renderer.backgroundColor = 0xefeff4;
app.renderer.view.style.display = "block";

document.body.appendChild(app.view);

var diagram = new PIXI.Container();
app.stage.addChild(diagram);

var info = {};
var best = {};
var last = {};
var version = {};
var boxes = [];
var playHover = null;
var lightInit = null;
var lightStop = null;
var textSize = 18;
var states = ["CODEC_FILTER", "SHUFFLE_SIZE",
  "THREADS", "CLEVEL", "BLOCKSIZE", "MEMCPY", "WAITING"];
var boxPositions = [
  180, 620,
  180, 501,
  180, 379,
  180, 256,
  180, 137,
  431, 69,
  513, 189];

// Load sprites
PIXI.loader
  .add(["img/background.png",
        "img/box1.png",
        "img/box1-h.png",
        "img/box2.png",
        "img/box2-h.png",
        "img/box3.png",
        "img/box3-h.png"
  ])
  .load(setup);

function setup() {
  let bgSprite = new PIXI.Sprite(
    PIXI.loader.resources["img/background.png"].texture
  );

  diagram.addChild(bgSprite);

  // Boxes List
  for (i = 0; i < (boxPositions.length / 2); i++) {
    var j = i * 2;
    var box = Box(states[i], boxPositions[j], boxPositions[j + 1]);
    diagram.addChild(box.graphics);
    boxes.push(box);
  }
  // Center
  diagram.x  = (app.renderer.width - bgSprite.width) / 2;
  diagram.y  = (app.renderer.height - bgSprite.height) / 2;

  // Init info
  var state = new PIXI.Text("INIT", {fontSize: 20});
  state.x = 82;
  state.y = 24;
  var readapt_type = new PIXI.Text("NONE", {fontSize: 20});
  readapt_type.x = 170;
  readapt_type.y = 54;
  var steps = new PIXI.Text("0", {fontSize: 20});
  steps.x = 86;
  steps.y = 85;
  diagram.addChild(state, readapt_type, steps);
  info.state = state;
  info.readapt_type = readapt_type;
  info.steps = steps;

  // Init best
  var best_score = new PIXI.Text("Score", {fontSize: textSize});
  best_score.x = 155;
  best_score.y = 150;
  best_score.anchor.set(1, 0);
  var best_cratio = new PIXI.Text("C.Ratio", {fontSize: textSize});
  best_cratio.x = 155;
  best_cratio.y = 180;
  best_cratio.anchor.set(1, 0);
  diagram.addChild(best_score, best_cratio);

  best.codec = boxes[0].graphics.children[3];
  best.filter = boxes[0].graphics.children[4];
  best.shufflesize = boxes[1].graphics.children[3];
  best.threads = boxes[2].graphics.children[3];
  best.clevel = boxes[3].graphics.children[3];
  best.blocksize = boxes[4].graphics.children[3];
  best.score = best_score;
  best.cratio = best_cratio;
  // Init last
  var last_score = new PIXI.Text("Score", {fontSize: textSize});
  last_score.x = 80;
  last_score.y = 150;
  last_score.anchor.set(1, 0);
  var last_cratio = new PIXI.Text("C.Ratio", {fontSize: textSize});
  last_cratio.x = 80;
  last_cratio.y = 180;
  last_cratio.anchor.set(1, 0);
  diagram.addChild(last_score, last_cratio);

  last.codec = boxes[0].graphics.children[5];
  last.filter = boxes[0].graphics.children[6];
  last.shufflesize = boxes[1].graphics.children[4];
  last.threads = boxes[2].graphics.children[4];
  last.clevel = boxes[3].graphics.children[4];
  last.blocksize = boxes[4].graphics.children[4];
  last.score = last_score;
  last.cratio = last_cratio;

  // Buttons
  var playButton = new PIXI.Graphics();
  playButton.lineStyle(2, 0x000000, 1);
  playButton.beginFill(0xffcc00, 1);
  playButton.drawRoundedRect(10, 10, 60, 60);
  playButton.lineStyle(1, 0x000000, 1);
  playButton.beginFill(0x282828, 1);
  playButton.drawPolygon([30,28, 30,52, 55,40]);
  playButton.endFill();
  playButton.x = bgSprite.width / 2 + 180;
  playButton.y = bgSprite.height - 90;
  playButton.buttonMode = true;
  playButton.interactive = true;
  playButton.on("pointerdown", playLog);
  diagram.addChild(playButton);

  playHover = new PIXI.Graphics();
  playHover.lineStyle(2, 0x000000, 1);
  playHover.beginFill(0xffcc00, 1);
  playHover.drawRoundedRect(10, 10, 60, 60);
  playHover.lineStyle(1, 0x000000, 1);
  playHover.beginFill(0x282828, 1);
  playHover.drawRect(30, 28, 6, 25);
  playHover.drawRect(45, 28, 6, 25);
  playButton.endFill();
  playHover.x = playButton.x;
  playHover.y = playButton.y;
  playHover.visible = false;
  diagram.addChild(playHover);

  var stopButton = new PIXI.Graphics();
  stopButton.lineStyle(2, 0x000000, 1);
  stopButton.beginFill(0xffcc00, 1);
  stopButton.drawRoundedRect(10, 10, 60, 60);
  stopButton.lineStyle(1, 0x000000, 1);
  stopButton.beginFill(0x282828, 1);
  stopButton.drawRect(28, 28, 24, 24);
  stopButton.endFill();
  stopButton.x = playButton.x - 65;
  stopButton.y = playButton.y;
  stopButton.buttonMode = true;
  stopButton.interactive = true;
  stopButton.on("pointerdown", stopLog);
  diagram.addChild(stopButton);

  var stepFwdButton = new PIXI.Graphics();
  stepFwdButton.lineStyle(2, 0x000000, 1);
  stepFwdButton.beginFill(0xffcc00, 1);
  stepFwdButton.drawRoundedRect(10, 10, 60, 60);
  stepFwdButton.beginFill(0x282828, 1);
  stepFwdButton.lineStyle(1, 0x000000, 1);
  stepFwdButton.drawPolygon([30,30, 30,50, 50,40]);
  stepFwdButton.drawRect(51, 30, 1, 20);
  stepFwdButton.endFill();
  stepFwdButton.x = playButton.x + 65;
  stepFwdButton.y = playButton.y;
  stepFwdButton.buttonMode = true;
  stepFwdButton.interactive = true;
  stepFwdButton.on("pointerdown", forwardLog);
  diagram.addChild(stepFwdButton);

  var stepBckButton = new PIXI.Graphics();
  stepBckButton.lineStyle(2, 0x000000, 1);
  stepBckButton.beginFill(0xffcc00, 1);
  stepBckButton.drawRoundedRect(10, 10, 60, 60);
  stepBckButton.beginFill(0x282828, 1);
  stepBckButton.lineStyle(1, 0x000000, 1);
  stepBckButton.drawPolygon([30,30, 30,50, 50,40]);
  stepBckButton.drawRect(51, 30, 1, 20);
  stepBckButton.endFill();
  stepBckButton.x = playButton.x - 65 * 2;
  stepBckButton.y = playButton.y;
  stepBckButton.pivot.set(80, 80);
  stepBckButton.rotation = Math.PI;
  stepBckButton.buttonMode = true;
  stepBckButton.interactive = true;
  stepBckButton.on("pointerdown", backwardLog);
  diagram.addChild(stepBckButton);

  lightInit = new PIXI.Graphics();
  lightInit.beginFill(0xff0000, 0.4);
  lightInit.drawCircle(43, 663, 32);
  lightInit.endFill();
  diagram.addChild(lightInit);
  lightInit.visible = true;

  lightStop = new PIXI.Graphics();
  lightStop.beginFill(0xff0000, 0.4);
  lightStop.drawCircle(710, 298, 32);
  lightStop.endFill();
  diagram.addChild(lightStop);
  lightStop.visible = false;

  version = new PIXI.Text("", {fontSize: 20});
  version.position.set(bgSprite.width - 122, bgSprite.height - 122);
  diagram.addChild(version);
}

function Box(name, x, y) {
  var aux = {};
  aux.graphics = new PIXI.Container();
  var g = aux.graphics;
  g.position.set(x, y);

  var text = new PIXI.Text(name, {fontSize: textSize, fontWeight: "600"});
  text.anchor.set(0.5, 0.5);

  if (name === "CODEC_FILTER") {
    var boxSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box1.png"].texture
    );
    var boxOnSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box1-h.png"].texture
    );
    text.position.set(110, 41);
    var best_codec = new PIXI.Text("", {fontSize: textSize});
    best_codec.anchor.set(0.5, 0.5);
    best_codec.position.set(151, 81);
    var best_filter = new PIXI.Text("", {fontSize: textSize});
    best_filter.anchor.set(0.5, 0.5);
    best_filter.position.set(151, 108);
    var last_codec = new PIXI.Text("", {fontSize: textSize});
    last_codec.anchor.set(0.5, 0.5);
    last_codec.position.set(69, 81);
    var last_filter = new PIXI.Text("", {fontSize: textSize});
    last_filter.anchor.set(0.5, 0.5);
    last_filter.position.set(69, 108);
    g.addChild(boxSprite, boxOnSprite, text, best_codec, best_filter, last_codec, last_filter);
  } else if (name === "MEMCPY" || name === "WAITING") {
    var boxSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box3.png"].texture
    );
    var boxOnSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box3-h.png"].texture
    );
    text.position.set(88, 36);
    g.addChild(boxSprite, boxOnSprite, text)
  } else {
    var boxSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box2.png"].texture
    );
    var boxOnSprite = new PIXI.Sprite(
      PIXI.loader.resources["img/box2-h.png"].texture
    );
    text.position.set(108, 38);
    var best_opt = new PIXI.Text("", {fontSize: textSize});
    best_opt.anchor.set(0.5, 0.5);
    best_opt.position.set(147, 80);
    var last_opt = new PIXI.Text("", {fontSize: textSize});
    last_opt.anchor.set(0.5, 0.5);
    last_opt.position.set(68, 80);
    g.addChild(boxSprite, boxOnSprite, text, best_opt, last_opt);
  }

  boxOnSprite.visible = false;
  return aux;
}

// Read Files
var btuneLog = null;
var logindex = 0;

// Load example
function loadExample() {
  var selection = document.getElementById("mySelect").value;
  var client = new XMLHttpRequest();
  client.open('GET', 'logs/' + selection);
  client.onreadystatechange = function() {
    processFile(client.responseText);
  }
  client.send();
}

// Input File
function readSingleFile(e) {
  var file = e.target.files[0];
  if (!file) {
    return;
  }
  var reader = new FileReader();
  reader.onload = function(e) {
    processFile(e.target.result);
  };
  reader.readAsText(file);
}

// Process file
function processFile(contents) {
  contents = contents.split("\n");
  var btuneConfig = "";
  let i = 1;
  let found = false;
  while(!found && i < contents.length) {
    if (contents[i].startsWith("-=-=-=")) {
        found = true;
        version.text = "v" + contents[i+1].split(":")[1].trim().slice(0, -1);
        btuneConfig = contents[i+2] + "\n" + contents[i+3];
        btuneLog = contents.slice(i+5, contents.length);
        logIndex = 0;
    }
    i++;
  }
  displayBtuneConfig(btuneConfig);
}

function displayBtuneConfig(config) {
  var element = document.getElementById("btune-config");
  element.textContent = config;
}

document.getElementById('file-input')
  .addEventListener('change', readSingleFile, false);

var interval = null;
function playLog() {
  playHover.visible = true;
  if (btuneLog !== null) {
    if (interval === null) {
      interval = setInterval(processLine, 1000);
    } else {
      pauseLog();
    }
  }
}

function processLine() {
  lightInit.visible = false;
  lightStop.visible = false;
  var line = btuneLog[logIndex];
  line = line.split("|");
  if (line.length == 1) {
    pauseLog();
    for (i = 0; i < boxes.length; i++) {
      boxes[i].graphics.children[0].visible = true;
      boxes[i].graphics.children[1].visible = false;
    }
    lightStop.visible = true;
  } else {
    updateCparams(last, line.slice(1, 10));
    if (line[12].trim() === "W") {
      updateCparams(best, line.slice(1, 10));
    }
    activateState(line[10].trim());
    info.state.text = line[10].trim();
    info.readapt_type.text = line[11].trim();
    info.steps.text = ++logIndex;
    if (logIndex == btuneLog.length) {
      pauseLog();
      for (i = 0; i < boxes.length; i++) {
        boxes[i].graphics.children[0].visible = true;
        boxes[i].graphics.children[1].visible = false;
      }
      lightStop.visible = true;
      info.state.text = "STOP";
    }
  }
}

function updateCparams(cparams, values) {
  cparams.codec.text = values[0].trim();
  let filter = "";
  if (values[1].trim() === "0") {
    filter = "noshuffle";
  } else if (values[1].trim() === "1") {
    filter = "shuffle";
  } else {
    filter = "bshuffle";
  }
  cparams.filter.text = filter;
  cparams.clevel.text = values[2].trim();
  cparams.blocksize.text = values[3].trim() + " kB";
  cparams.shufflesize.text = values[4].trim();
  cparams.threads.text = values[5].trim() + "C | " + values[6].trim() + "D";
  var score = parseFloat(values[7].trim());
  if (score < 0.001) {
    cparams.score.text = score.toExponential(2);
  } else {
    cparams.score.text = score.toFixed(3);
  }
  cparams.cratio.text = parseFloat(values[8].trim()).toString() + "x";
}

function activateState(state) {
  for (i = 0; i < boxes.length; i++) {
    boxes[i].graphics.children[0].visible = true;
    boxes[i].graphics.children[1].visible = false;
  }
  let j = 0;
  if (state.startsWith("THREAD")) {
    j = 2;
  } else {
    j = states.indexOf(state);
  }
  boxes[j].graphics.children[0].visible = false;
  boxes[j].graphics.children[1].visible = true;
}

function pauseLog() {
  clearInterval(interval);
  interval = null;
  playHover.visible = false;
}

function stopLog() {
  pauseLog();
  for (i = 0; i < boxes.length; i++) {
    boxes[i].graphics.children[0].visible = true;
    boxes[i].graphics.children[1].visible = false;
  }
  lightInit.visible = true;
  lightStop.visible = false;
  logIndex = 0;
  info.state.text = "INIT";
  info.readapt_type.text = "NONE";
  info.steps.text = "0";
  boxes[0].graphics.children[3].text = "";
  boxes[0].graphics.children[4].text = "";
  boxes[0].graphics.children[5].text = "";
  boxes[0].graphics.children[6].text = "";
  boxes[1].graphics.children[3].text = "";
  boxes[1].graphics.children[4].text = "";
  boxes[2].graphics.children[3].text = "";
  boxes[2].graphics.children[4].text = "";
  boxes[3].graphics.children[3].text = "";
  boxes[3].graphics.children[4].text = "";
  boxes[4].graphics.children[3].text = "";
  boxes[4].graphics.children[4].text = "";
  best.score.text = "Score";
  last.score.text = "Score";
  best.cratio.text = "C.Ratio";
  last.cratio.text = "C.Ratio";
}

function forwardLog() {
  if (logIndex != btuneLog.length) {
    processLine();
  }
}

function backwardLog() {
  logIndex -= 2;
  if (logIndex < 0) {
    stopLog();
  } else {
    processLine();
  }
}
