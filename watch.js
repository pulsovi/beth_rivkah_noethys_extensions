const beep = require('beepbeep');
const fs = require('fs');
const path = require('path');
const destinationFolder = "C:\\Users\\DHG\\AppData\\Roaming\\noethys\\Extensions";
const { fork, exec } = require('child_process');
const timeouts = [];
const child_process = require("child_process");
const Registry = require("winreg");

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
    "DLG_Famille_maj_resultats_calcules.py",
  ];
  const toIgnore = [
    ".git",
    "Appliquer_tarifs_convenus.py",
    "Calcul_totaux_infos_financ.py",
    "Debug_extensions.py",
    "Exporter_anomalies.py",
    "anomalies.sql",
    "divers.py",
    "inscription nouvelle annee.sql",
    "reset extensions auto.sh",
  ];
  if (file === "watch.js") {
    console.log("exit child");
    process.exit();
    return
  }
  if (toSend.includes(file)) return send(file);
  if (toIgnore.includes(file)) return;
  if (file === "NoethysLogIn.ahk") return restartAHK();
  beep();
  console.log(`Wath to do on change file: ${file} ?`);
}

function restartAHK() {
  const timeout = timeouts.find(to => to.action === "restartAHK")
  if (timeout) {
    clearTimeout(timeout.timeout);
    timeout.timeout = setTimeout(() => performRestartAHK(), 200);
    return;
  }
  timeouts.push({ action: "restartAHK", timeout: setTimeout(() => performRestartAHK(), 200) });
}

async function performRestartAHK() {
  const ahkPath = path.join(__dirname, "NoethysLogIn.ahk");
  const ahkExePath = await new Promise((resolve, reject) => {
    const regKey = new Registry({hive: Registry.HKLM, key: "\\SOFTWARE\\AutoHotkey"});
    regKey.values((err, items) => {
      if (err) return reject(err);
      const item = items.find(itm => itm.name === "InstallDir");
      resolve(path.join(item.value, "AutoHotkeyU64.exe"));
    })
  });
  child_process.exec(`"${ahkExePath}" "${ahkPath}"`, err => {
    if (err) console.log("AHK reload error:\n", err);
  });
}

function send(file) {
  const timeout = timeouts.find(to => to.action === "send" && to.file === file)
  if (timeout) {
    clearTimeout(timeout.timeout);
    timeout.timeout = setTimeout(() => performSend(file), 200);
    return;
  }
  timeouts.push({ action: "send", file, timeout: setTimeout(() => performSend(file), 200) });
}

function performSend(file) {
  const index = timeouts.findIndex(f => f.file === file);
  timeouts.splice(index, 1);
  fs.copyFile(
    path.join(__dirname, file),
    path.join(destinationFolder, file),
    (err) => {
      console.log(`sended ${file}`, {err});
      restartNoethys();
    }
  )
}

async function runWatch() {
  await sleep(1000);
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
  return new Promise(resolve => childProcess.once('exit', (...args) => resolve(...args)));
}

if (process.send) watch();
else runWatch();
