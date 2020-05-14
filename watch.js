const beep = require('beepbeep');
const fs = require('fs');
const path = require('path');
const destinationFolder = "C:\\Users\\DHG\\AppData\\Roaming\\noethys\\Extensions";
const { fork, exec } = require('child_process');
const toSend = [];

function watch() {
  console.log("start child");
  fs.watch(__dirname, (event, file) => {
    switch (event) {
    case "change":
      handleChange(file);
      break;
    case "rename":
      break;
    default:
      beep();
      console.log(`unknown event ${event}, (filename: ${file})`);
      break;
    }
  });
}

function handleChange(file) {
  //console.log(`change ${file}`);
  const toSend = [
    "CTRL_Famille_outils.py",
    "DLG_Famille_evaluer_mensualite.py",
    "Extensions_automatiques.py",
    "DLG_Famille_bouton_maj_resultats_calcules.py",
  ];
  const toIgnore = [
    ".git",
    "Appliquer_tarifs_convenus.py",
    "Calcul_totaux_infos_financ.py",
    "Debug_extensions.py",
    "Exporter_anomalies.py",
    "divers.py",
  ];
  if (file === "watch.js") {
    console.log("exit child");
    process.exit();
    return
  }
  if (toSend.includes(file)) return send(file);
  if (toIgnore.includes(file)) return;
  beep();
  console.log(`Wath to do on change file: ${file} ?`);
}

function send(file) {
  const to = toSend.find(f => f.file === file)
  if (to) {
    clearTimeout(to.to);
    to.to = setTimeout(() => performSend(file), 200);
    return;
  }
  toSend.push({ file, to: setTimeout(() => performSend(file), 200) });
}

function performSend(file) {
  const index = toSend.findIndex(f => f.file === file);
  toSend.splice(index, 1);
  fs.copyFile(
    path.join(__dirname, file),
    path.join(destinationFolder, file),
    (err) => {
      console.log(`sended ${file}`, {err});
      restartNoethys();
    }
  )
}

function runWatch() {
  fork(__filename).once('exit', runWatch);
}

async function restartNoethys() {
  await waitForProcess(exec('TASKKILL /T /IM Noethys.exe'));
  await sleep(200);
  exec('C:\\Noethys\\Noethys.exe')
}

function sleep(delay) {
  return new Promise(resolve => setTimeout(resolve, delay));
}

function waitForProcess(childProcess) {
  //console.log('childProcess:', childProcess.spawnargs.join(" "));
  return new Promise(resolve => childProcess.once('exit', (...args) => resolve(...args)));
}

if (process.send) watch();
else runWatch();
