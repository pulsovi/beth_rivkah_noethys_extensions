const fs = require('fs');
const child_process = require("child_process");
const { promisify } = require("util");


const extensions = [
  "Calcul_totaux_infos_financ.py",
  "CTRL_Famille_outils.py",
  "DLG_Famille_evaluer_mensualite.py",
  "DLG_Famille_fixer_tarif.py",
  "Extensions_automatiques.py",
  "Mensualite_base.py",
  "Utils__init__.py",
];

const commit_content = child_process.execSync("git status --porcelain").toString().split("\n");
const oldVersions = getOldVersions();
const versions = {};

async function getIndexed(filename) {
  const exec = promisify(child_process.exec);
  const { stdout } = await exec(`git cat-file --textconv -- :${filename}`).catch(err => {
    if (err) {
      console.log(err);
      process.exit(1);
    }
  });
  return stdout
}

function getOldVersions() {
  const stdout = child_process
    .execSync("git cat-file --textconv -- HEAD:versions.json")
    .toString();
  return JSON.parse(stdout);
}

async function getVersion(filename) {
  if (!isModified(filename) && oldVersions[filename]) return oldVersions[filename];
  const content = await getIndexed(filename);
  const lines = content.split("\n");
  const line = lines.find(l => l.includes("VERSION ="));
  if (!line) {
    //console.log({content, filename, lines, line});
    throw new Error(`Cannot find the VERSION line in ${filename}`);
  }
  return line.split('"')[1];
}

function isModified(filename) {
  const line = commit_content.find(line => line.includes(filename));
  if (!line) return false;
  if (line[0] === "M" || line[0] === "A") return true;
  return false;
}

async function main() {
  await Promise.all(extensions.map(
    filename => getVersion(filename).then(
      version => versions[filename] = version
    )
  )).catch(err => {
    console.log(err);
    process.exit(1);
  });

  extensions.forEach(filename => {
    if (isModified(filename) && oldVersions[filename] === versions[filename]) {
      console.log(`${filename} est modifié mais le numéro de version n'a pas évolué`);
      process.exit(1);
    }
  });

  fs.writeFile("./versions.json", JSON.stringify(versions, null, 2), "utf8", err => {
    if (err) {
      console.log(err);
      process.exit(1);
    }
  });
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
