/* State: */
var speechTracking = false;
var workerAvailable = false;
var validating = false;
var cursorPos = 0;
var writingCustom = false;
var ReadingPrompt = function() {
  var asList = [];
  var asHTMLList = [];
  var lastSpace = null;
  this.loadText = function(text) {
    asList = text.split(/(\s+)/).filter( function(x) {return x.trim().length > 0;});
    asHTMLList = [];
    for (i = 0; i < asList.length; i++) {
      var spaceSpan = document.createElement('span');
      var wordSpan = document.createElement('span');
      spaceSpan.innerHTML = " ";
      spaceSpan.classList.add('promptspace');
      wordSpan.innerHTML = asList[i];
      wordSpan.classList.add('promptword');
      asHTMLList.push({//div: wordDiv, 
        spaceSpan: spaceSpan,
        wordSpan: wordSpan});
    }
    lastSpace = document.createElement('span');
    lastSpace.innerHTML = " ";
    lastSpace.classList.add('promptspace');
  }
  this.getHTMLList = function() {
    return asHTMLList;
  }
  this.getWordAtIndex = function(index) {
    return asHTMLList[index].wordSpan;
  }
  this.getBareWordAtIndex = function(index) {
    return asList[index];
  }
  this.getLastSpace = function() {
    return lastSpace;
  }
};
function setupPromptDiv(readingPrompt) {
  var HTMLList = readingPrompt.getHTMLList();
  var lastSpace = readingPrompt.getLastSpace();
  var promptdiv = document.getElementById("prompt")
  promptdiv.innerHTML = "";
  for (i = 0; i < HTMLList.length; i++) {
    promptdiv.appendChild(HTMLList[i].spaceSpan);
    promptdiv.appendChild(HTMLList[i].wordSpan);
  }
  promptdiv.appendChild(lastSpace);
}

var readingPrompt = new ReadingPrompt();

var dictate = new Dictate({
  server : server_url,
  serverStatus : status_server_url,
  recorderWorkerPath : recorder_worker_url,
  graph_id : "<unknown>",
  record_cookie : "<unknown>",
  onPartialResults : function(result) {
    bestHypothesis = result.result.hypotheses[0].transcript;
    __processHypothesis(bestHypothesis);
  },
  onResults : function(result) {
    setInstruction("Validating.");
    bestHypothesis = result.result.hypotheses[0].transcript;
    __processHypothesis(bestHypothesis);
    startValidating();
    verdict = result["validation-verdict"];
    reason = result["validation-reason"];
    if (verdict) {
      showAccepted();
    }
    else {
      showRejected(reason);
    }
  },
  onServerStatus : function(json) {
    if (json.num_workers_available == 0) {
      workerAvailable = false;
    } else {
      workerAvailable = true;
    }
  }
});
function setupPrompt() {
  //Reset state: 
  speechTracking = false;
  validating = false;
  cursorPos = 0;
  writingCustom = false;
  readingPrompt.loadText(prompt_text);
  setupPromptDiv(readingPrompt);
  setInstruction('Press and hold <span class="teletype">&lt;space&gt;</span>');
  dictate.getConfig()["graph_id"] = graph_id;
  dictate.getConfig()["record_cookie"] = record_cookie;
}
setupPrompt()

/* callbacks for dictate */
function __processHypothesis(hypothesis) {
  console.log("Got hypo");
  console.log(hypothesis);
  parsedHypo = parseHypothesis(hypothesis);
  colorPrompt(readingPrompt, parsedHypo);
  blinkCursor();
}

function startValidating() {
  validating = true;
  /*var hider = document.getElementById('prompthider');
  hider.classList.add("show");*/
  var HTMLList = readingPrompt.getHTMLList();
  for (index = 0; index < HTMLList.length; index++) {
    HTMLList[index].wordSpan.classList.add('validating')
  }
  //document.getElementById("readbutton").classList.add("pure-button-disabled")
}

function validate(hypothesis, parsedHypothesis) {
  var HTMLList = readingPrompt.getHTMLList();
  var jumps = 0;
  var lastcorrect = -1;
  var garbages = 0;
  var truncations = 0;
  var hypolist = hypothesis.split(/(\s+)/).filter( function(x) {return x.trim().length > 0;});
  var formattedHypo = document.createElement('div');
  var latestOccurrences = {};
  for (var i = 0; i < hypolist.length; i++) {
    if (hypolist[i] === '<garbage>') {
      garbages += 1;
      var spanner = document.createElement('span');
      spanner.innerHTML = '[spoken noise] ';
      spanner.classList.add('spn');
      formattedHypo.appendChild(spanner);
      continue
    }
    else if (hypolist[i].split(':')[0] === 'trunc') {
      index = hypolist[i].split('@')[1]
      truncations += 1;
      var spanner = document.createElement('span');
      spanner.innerHTML = '[truncated ' + readingPrompt.getBareWordAtIndex(index) + '] ';
      spanner.classList.add('trunc');
      formattedHypo.appendChild(spanner);
      continue
    }
    else if (lastcorrect + 1 !== parseInt(hypolist[i].split('@')[1])) {
      var spanner = document.createElement('span');
      spanner.innerHTML = '[jump] ';
      spanner.classList.add('jump');
      formattedHypo.appendChild(spanner);
      jumps += 1;
    }
    index = parseInt(hypolist[i].split('@')[1])
    var spanner = document.createElement('span');
    spanner.innerHTML = readingPrompt.getBareWordAtIndex(index) + " ";
    spanner.classList.add('correct');
    if (latestOccurrences.hasOwnProperty(index)) {
      latestOccurrences[index].classList.remove('correct');
    }
    latestOccurrences[index] = spanner;
    formattedHypo.appendChild(spanner);
    lastcorrect = index;
  }
  for (index = 0; index < HTMLList.length; index++) {
    cls = getReadingClassByIndex(parsedHypothesis, index);
    if (cls !== 'correct') {
      console.log("Reject")
      showRejected('All words were not found', formattedHypo);
      return;
    }
  } 
  if (jumps > 5) {
    console.log("Reject");
    showRejected('Too many miscues detected', formattedHypo);
    return;
  }
  if (garbages > 10) {
    console.log("Reject");
    showRejected('Too much spoken noise detected', formattedHypo);
    return;
  }
  console.log("Accept")
  showAccepted(formattedHypo);
}

function getReloadButton(button_text) {
  var button = document.createElement('button');
  button.classList.add("pure-button");
  button.onclick = function() { window.location.reload(true);}
  button.innerHTML = button_text;
  button.focus();
  return button
}

function showRejected(reasontext) {
  var popup = document.getElementById('popup');
  popup.innerHTML = "";
  var verdict = document.createElement('div');
  verdict.innerHTML = '<h2 class="boo">Validation: reject</h2>';
  var reason = document.createElement('div');
  reason.innerHTML = reasontext;
  popup.appendChild(verdict);
  popup.appendChild(reason);
  button = getReloadButton("Try again");
  popup.appendChild(button);
  popup.classList.add("show");
}

function showAccepted() {
  var popup = document.getElementById('popup');
  popup.innerHTML = "";
  var verdict = document.createElement('div');
  verdict.innerHTML = '<h2 class="yeah">Validation: accept</h2>';
  popup.appendChild(verdict);
  button = getReloadButton("Next!");
  popup.appendChild(button);
  popup.classList.add("show");
}


function setReadingClass(element, cls) {
  element.classList.remove('correct');
  element.classList.remove('truncated');
  element.classList.remove('missed');
  if (cls !== null) {
    element.classList.add(cls);
  }
}
function getReadingClassByIndex(parsedHypo, index) {
  if (parsedHypo.correctInds.has(index)) {return 'correct';}
  if (parsedHypo.truncInds.has(index)) {return 'truncated';}
  if (parsedHypo.missedInds.has(index)) {return 'missed';}
  return null;
}

function colorPrompt(readingPrompt, parsedHypothesis) {
  var HTMLList = readingPrompt.getHTMLList();
  for (index = 0; index < HTMLList.length; index++) {
    cls = getReadingClassByIndex(parsedHypothesis, index);
    setReadingClass(HTMLList[index].wordSpan, cls);
    if (speechTracking) {
      HTMLList[index].wordSpan.classList.remove('future');
      HTMLList[index].wordSpan.classList.remove('past');
      if (index >= parsedHypothesis.cursor + 1) {
        HTMLList[index].wordSpan.classList.add('future');
      }
      if (index < parsedHypothesis.cursor) {
        HTMLList[index].wordSpan.classList.add('past');
      }
    }
  }
  cursorPos = parsedHypothesis.cursor;
}

function colorAtStart(readingPrompt) {
  var HTMLList = readingPrompt.getHTMLList();
  for (index = 1; index < HTMLList.length; index++) {
    HTMLList[index].wordSpan.classList.add('future');
  }
  cursorPos = 0;
}
function colorAtEnd(readingPrompt) {
  var HTMLList = readingPrompt.getHTMLList();
  for (index = 0; index < HTMLList.length; index++) {
    HTMLList[index].wordSpan.classList.remove('future');
    HTMLList[index].wordSpan.classList.remove('past');
  }
}

var cursorOn = false;
function blinkCursor() {
  var HTMLList = readingPrompt.getHTMLList();
  for (i = 0; i < HTMLList.length; i++) {
    if (cursorPos === i) {
      if (speechTracking && !cursorOn) {
        cursorOn = true;
        HTMLList[i].spaceSpan.classList.add('blink');
      }
      else {
        HTMLList[i].spaceSpan.classList.remove('blink');
        cursorOn = false;
      }
    }
    else {
      HTMLList[i].spaceSpan.classList.remove('blink');
    }
  }
  var lastSpace = readingPrompt.getLastSpace();
  if (cursorPos === HTMLList.length) {
    if (speechTracking && !cursorOn) {
      cursorOn = true;
      lastSpace.classList.add('blink');
    }
    else {
      lastSpace.classList.remove('blink');
      cursorOn = false;
    }
  } 
  else {
    lastSpace.classList.remove('blink');
  }
}
window.setInterval(blinkCursor, 300);

function parseHypothesis(hypothesis) {
  var parsed = {correctInds: new Set(), truncInds: new Set(), missedInds: new Set(), cursor: 0};
  var reTruncInds = /(?:^|\s)trunc:[^@]*@([0-9]*)/g;
  var reCorrectInds = /(?:^|\s)(?!trunc:)[^@]*@([0-9]*)/g;
  var triedWords = []; 
  var reresult;
  while ((reresult = reCorrectInds.exec(hypothesis)) !== null) {
    index = parseInt(reresult[1]);
    parsed.correctInds.add(index);
    parsed.cursor = index + 1;
    triedWords.push(index);
  }
  while ((reresult = reTruncInds.exec(hypothesis)) !== null) {
    index = parseInt(reresult[1]);
    if (!parsed.correctInds.has(index)) {
      parsed.truncInds.add(index);
      triedWords.push(index);
    }
  }
  triedWords.sort(function (a,b) { return a - b; });
  triedSet = new Set(triedWords);
  for (i=0; i < triedWords[triedWords.length-1]; i++) {
    if (!triedSet.has(i)) {
      parsed.missedInds.add(i);
    }
  }
  var hyposplit = hypothesis.split(" ")
  if (hyposplit[hyposplit.length - 1] === "<garbage>") {
    parsed.truncInds.add(parsed.cursor);
  }
  return parsed;
}

function setInstruction(text) {
  //Disabled for now:
  return;
  //instruction = document.getElementById('instruction');
  //instruction.innerHTML = text;
}

function startTracking() {
  if (!workerAvailable) {
    console.log("Worker not available.");
    setInstruction("Wait for the recogniser to become ready.");
    return;
  }
  console.log("Starting speech tracking.");
  try{
    dictate.startListening();
    speechTracking = true;
    __processHypothesis(""); 
    colorAtStart(readingPrompt);
    setInstruction("Read the prompt aloud. The speech recogniser tries track you and shows where it predicts you are.")
  } catch (e) {
    console.log("Unable to start speech tracking due to error: " +e);
    speechTracking = false;
    colorAtEnd(readingPrompt);
    setInstruction("Could not start speech tracking. Try again?");
  }
}
function stopTracking() {
  console.log("Stopping speech tracking.");
  dictate.stopListening();
  speechTracking = false;
  colorAtEnd(readingPrompt);
  setInstruction("Waiting for final recogniser output.")
}

function setupCustomPrompt(text, xhttp) {
  speechTracking = false;
  validating = false;
  cursorPos = 0;
  writingCustom = false;
  readingPrompt.loadText(text);
  setupPromptDiv(readingPrompt);
  setInstruction('Custom prompt graph ready. Press and hold <span class="teletype">&lt;space&gt;</span>');
  dictate.getConfig()["graph_id"] = "custom";
}

function createCustomPromptGraph(text) {
  setInstruction("Waiting for the decoging graph compilation");
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (this.responseText == "FAILED") {
        setInstruction("Graph creation failed. Sorry.")
      }
      else {
        setupCustomPrompt(text, this);
      }
    }
  };
  xhttp.open("POST", "/custom-graph", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("text="+text);
}

function makeYourOwn() {
  //var hider = document.getElementById('prompthider');
  //hider.classList.remove('show');
  var popup = document.getElementById('popup');
  popup.classList.remove('show');

  console.log("Started making my own prompt.");
  setInstruction("Write your prompt and press enter.");
  var promptdiv = document.getElementById('prompt');
  promptdiv.innerHTML = "";
  var promptEntry = document.createElement('INPUT');
  promptEntry.setAttribute("type", "textarea");
  promptEntry.classList.add("promptEntry");
  promptEntry.onkeydown = function(evt) {
    if (evt.keyCode == 13) {
      createCustomPromptGraph(promptEntry.value)
      return false;
    }
  };
  promptdiv.appendChild(promptEntry);
  promptEntry.focus();
  writingCustom = true;
}



document.onkeydown = function(evt) {
  evt = evt || window.event;
  if (evt.keyCode == 32) { 
    if (!speechTracking && !validating && !writingCustom) {
      startTracking();
    }
    return false;
  }
};

document.onkeyup = function(evt) {
  evt = evt || window.event;
  if (evt.keyCode == 32 && speechTracking && !validating && !writingCustom) {
    stopTracking();
  }
  else if (evt.keyCode == 32 && !validating && !writingCustom) {
    setInstruction('Press and hold <span class="teletype">&lt;space&gt;</span>')
  }
};


function startListening() {
	dictate.startListening();
}

function stopListening() {
	dictate.stopListening();
}

window.onload = function() {
  dictate.init();
  //btn = document.getElementById("readbutton");
  ///btn.onmousedown = btn.ontouchstart = function(evt) {
  //  if (!speechTracking && !validating && !writingCustom) {
  //    startTracking();
  //  }
  //}
  //btn.onmouseup = btn.ontouchend = function(evt) {
  //  if (speechTracking && !validating && !writingCustom) {
  //    stopTracking();
  //  }
  //}
}
