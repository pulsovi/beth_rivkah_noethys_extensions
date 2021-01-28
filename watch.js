const beep = require('beepbeep');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const destinationFolder = "C:\\Users\\DHG\\AppData\\Roaming\\noethys\\Extensions";
const timeouts = [];
const { fork, exec } = require("child_process");
const Registry = require("winreg");
const { noethysPath, pythonPath } = require("./config.json");

const Reset = "\x1b[0m";
const Bright = "\x1b[1m";
const Dim = "\x1b[2m";
const Underscore = "\x1b[4m";
const Blink = "\x1b[5m";
const Reverse = "\x1b[7m";
const Hidden = "\x1b[8m";

const FgBlack = "\x1b[30m";
const FgRed = "\x1b[31m";
const FgGreen = "\x1b[32m";
const FgYellow = "\x1b[33m";
const FgBlue = "\x1b[34m";
const FgMagenta = "\x1b[35m";
const FgCyan = "\x1b[36m";
const FgWhite = "\x1b[37m";

const BgBlack = "\x1b[40m";
const BgRed = "\x1b[41m";
const BgGreen = "\x1b[42m";
const BgYellow = "\x1b[43m";
const BgBlue = "\x1b[44m";
const BgMagenta = "\x1b[45m";
const BgCyan = "\x1b[46m";
const BgWhite = "\x1b[47m";

(() => {
  console.nativeLog = console.log;
  console.log = (...args) => console.nativeLog(new Date().toLocaleTimeString(), ...args);
})();

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
    "ext_Calcul_totaux_infos_financ.py",
    "ext_CTRL_Famille_outils.py",
    "ext_Debug_SQL.py",
    "ext_DLG_Famille_evaluer_mensualite.py",
    "ext_DLG_Famille_fixer_tarif.py",
    "ext_DLG_Famille_maj_resultats_calcules.py",
    "ext_DLG_Liste_inscriptions.py",
    "ext_Extensions_automatiques.py",
    "ext_Preparer_Export.py",
    "ext_Tests.py",
  ];
  const toIgnore = [
    ".git",
    ".gitignore",
    "anomalies.sql",
    "Appliquer_tarifs_convenus.py",
    "config.json",
    "config.json.dist",
    "Debug_extensions.py",
    "divers.py",
    "Exporter_anomalies.py",
    "inscription nouvelle annee.sql",
    "maj_versions.js",
    "node_modules",
    ".goutputstream-*",
    "questions.csv",
    "reset extensions auto.sh",
    "TODOS.txt",
    "Utils__init__.pyc",
    "versions.json",
  ];
  if (file === "watch.js" || file === "config.json") {
    console.log("exit child");
    process.exit();
    return;
  }
  if (file === "Utils__init__.py") {
    exec(
      `"${pythonPath}" -m compileall -f Utils__init__.py`,
      err => console.log("Utils/__init__.pyc compiled", {err})
    );
    return;
  }
  if (toSend.includes(file)) return send(file);
  if (toIgnore.includes(file)) return;
  if (file === "NoethysLogIn.ahk") return restartAHK();
  beep();
  console.log(`${FgRed}Wath to do on change file: ${file} ?${Reset}`);
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
  exec(`"${ahkExePath}" "${ahkPath}"`, err => {
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
  let retval = 0;
  while (!retval)
    retval = await waitForProcess(exec('TASKKILL /T /F /IM Noethys.exe'));
  await sleep(200);
  await clearNoethysLog();
  exec('Noethys.exe', { cwd: noethysPath })
}

function clearNoethysLog() {
  return new Promise((resolve, reject) => {
    fs.truncate('C:\\Noethys\\Noethys.exe.log', err => {
      if (err) reject(err);
      resolve();
    });
  });
}

function sleep(delay) {
  return new Promise(resolve => setTimeout(resolve, delay));
}

function waitForProcess(childProcess) {
  return new Promise(resolve => childProcess.once('exit', (...args) => resolve(...args)));
}

if (process.send) watch();
else runWatch();
