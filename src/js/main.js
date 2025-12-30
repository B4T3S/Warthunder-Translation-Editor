// Import all of Bootstrap's JS
import * as bootstrap from "bootstrap";
import $ from "jquery";
import Papa from "papaparse";
import Database from "./database";
import debounce from "lodash.debounce";

let gameFiles = {};
let languages = [
  "English",
  "French",
  "Italian",
  "German",
  "Spanish",
  "Russian",
  "Polish",
  "Czech",
  "Turkish",
  "Chinese",
  "Japanese",
  "Portuguese",
  "Ukrainian",
  "Serbian",
  "Hungarian",
  "Korean",
  "Belarusian",
  "Romanian",
  "TChinese",
  "HChinese",
  "Vietnamese",
];
let dbInterface = new Database();

// SETUP BLOCK

$(document).ready(() => {
  $(folderPicker).on("click", function () {
    window
      .showDirectoryPicker({
        id: "wtDir",
        mode: "readwrite",
      })
      .then(function (directory) {
        verifyDirectory(directory);
      });
  });

  $(updateConfigButton).on("click", function () {
    gameFiles["config.blk"].getFile().then((file) => {
      file.text().then((content) => {
        // Update the configuration file
        let newContent;
        const debugRegex = /debug\s*\{[^{}]*\}/;
        if (debugRegex.test(content)) {
          newContent = content.replace(debugRegex, (match) => {
            return match.includes("testLocalization:b=yes")
              ? match
              : match.replace(/\}$/, "  testLocalization:b=yes\n}");
          });
        } else {
          newContent = content + "\ndebug {\n    testLocalization:b=yes\n}";
        }

        // Write the new content to the configuration file
        gameFiles["config.blk"].createWritable().then((writable) => {
          writable.write(newContent).then(() => {
            writable.close();
            setTimeout(async () => {
              verifyConfiguration(await gameFiles["config.blk"].getFile());
            }, 500);
          });
        });
      });
    });
  });

  $("#editChangeSearchInput").on(
    "input",
    debounce(() => {
      updateAdditionTable();
    }, 350),
  );

  $(checkFilesButton).on("click", verifyLangFolderExists);

  $(editChangeLangSelect).on("change", function () {
    updateAdditionTable();
  });

  $("#editChangeResetSearchButton").on("click", () => {
    $("#editChangeSearchInput").val("");
    updateAdditionTable();
  });
});

// END SETUP BLOCK

// CONFIG BLOCK

function verifyDirectory(directory) {
  var entries = {};

  Array.fromAsync(
    directory.entries(),
    (element) => (entries[element[0]] = element[1]),
  ).then(() => {
    if (entries["config.blk"] != undefined) {
      gameFiles = entries;

      // Success, show the next step
      $("#locateGameHeader .spinner-border").attr("hidden", true);
      $("#locateGameHeader .bi-check-lg").attr("hidden", false);
      $("#locateGameHeader .bi-x-lg").attr("hidden", true);
      $("#wrongGamePath").attr("hidden", true);
      $("#locateGameCollapse input").attr("value", directory.name);

      setTimeout(async () => {
        $("#checkConfigHeader > button").attr("disabled", false);
        $("#checkConfigHeader > button").trigger("click");
        $("#checkConfigHeader > button").attr("disabled", true);
        $("#checkConfigHeader .spinner-border").attr("hidden", false);

        verifyConfiguration(await entries["config.blk"].getFile());
      }, 500);
    } else {
      // Failure, show the error message
      $("#locateGameHeader .spinner-border").attr("hidden", true);
      $("#locateGameHeader .bi-check-lg").attr("hidden", true);
      $("#locateGameHeader .bi-x-lg").attr("hidden", false);
      $("#wrongGamePath").attr("hidden", false);
    }
  });
}

function verifyConfiguration(configFile) {
  configFile.text().then((content) => {
    const regex = /debug\s*\{[^{}]*\btestLocalization:b=yes\b[^{}]*\}/;
    if (regex.test(content)) {
      // Success, show the next step
      $("#checkConfigHeader .spinner-border").attr("hidden", true);
      $("#checkConfigHeader .bi-check-lg").attr("hidden", false);
      $("#checkConfigHeader .bi-x-lg").attr("hidden", true);
      $("#checkConfigText").attr("hidden", true);
      $("#checkConfigTextSuccess").attr("hidden", false);
      $("#checkConfigTextFail").attr("hidden", true);

      setTimeout(async () => {
        $("#checkFilesHeader > button").attr("disabled", false);
        $("#checkFilesHeader > button").trigger("click");
        $("#checkFilesHeader > button").attr("disabled", true);
        $("#checkFilesHeader .spinner-border").attr("hidden", false);

        verifyLangFolderExists();
      }, 500);
    } else {
      // Failure, prompt the user to fix the configuration file
      $("#checkConfigHeader .spinner-border").attr("hidden", true);
      $("#checkConfigHeader .bi-check-lg").attr("hidden", true);
      $("#checkConfigHeader .bi-x-lg").attr("hidden", false);
      $("#checkConfigText").attr("hidden", true);
      $("#checkConfigTextSuccess").attr("hidden", true);
      $("#checkConfigTextFail").attr("hidden", false);
    }
  });
}

function verifyLangFolderExists() {
  if (gameFiles["lang"]?.kind == "directory") {
    // Success, show the next step
    $("#checkFilesHeader .spinner-border").attr("hidden", true);
    $("#checkFilesHeader .bi-check-lg").attr("hidden", false);
    $("#checkFilesHeader .bi-x-lg").attr("hidden", true);
    $("#checkFilesText").attr("hidden", true);
    $("#checkFilesTextSuccess").attr("hidden", false);
    $("#checkFilesTextFail").attr("hidden", true);

    setTimeout(async () => {
      $("#configWindow").attr(
        "style",
        "transition-duration: .75s; top: -105vh",
      );

      const files = await Array.fromAsync(await gameFiles["lang"].values());
      const tasks = files.map(async (entry) => {
        return openCSV(await entry.getFile());
      });

      Promise.all(tasks).then(() => {
        console.log("ALL FILES LOADED!");

        const modal = document.getElementById("editChangeLangSelect");
        languages.forEach((lang) => {
          const option = document.createElement("option");
          option.value = lang;
          option.innerText = lang;
          modal.appendChild(option);
        });

        bootstrap.Toast.getOrCreateInstance($("#filesLoadedToast"), {
          autohide: true,
          delay: 3000,
        }).show();

        updateAdditionTable();
      });
    }, 500);
  } else {
    // Failure, prompt the user to start the game
    $("#checkFilesHeader .spinner-border").attr("hidden", true);
    $("#checkFilesHeader .bi-check-lg").attr("hidden", true);
    $("#checkFilesHeader .bi-x-lg").attr("hidden", false);
    $("#checkFilesText").attr("hidden", true);
    $("#checkFilesTextSuccess").attr("hidden", true);
    $("#checkFilesTextFail").attr("hidden", false);
  }
}

// END CONFIG BLOCK

// MAIN BLOCK

class Change {
  translation_id = "";
  original = "";
  changed = "";
  language = "";

  constructor(translation_id, original, changed, language) {
    this.translation_id = translation_id;
    this.original = original;
    this.changed = changed;
    this.language = language;
  }
}

function openCSV(file) {
  return new Promise((resolve) => {
    Papa.parse(file, {
      header: true,
      complete: function (results) {
        console.log(
          "Loaded " + file.name + " with " + results.data.length + " rows",
        );

        dbInterface.addTranslationFile(file.name, results.data, languages);

        resolve();
      },
    });
  });
}

function updateAdditionTable(page = 0) {
  const table = $(editChangeTBody);
  const lang = $("#editChangeLangSelect").find(":selected").text();
  const query = $("#editChangeSearchInput").val();

  table.html("");

  const result = dbInterface.getPaginatedSearchResults(lang, query, page);

  result.forEach((res, index) => {
    const row = $(`
      <tr id="row-${index}">
        <th scope="row" class="text-truncate" style="max-width: 250px;">${res[0]}</th>
        <td><input type="text" class="w-100" /></td>
        <td><button class="btn btn-success"><i class="bi bi-floppy-fill"></i></button></td>
      </tr>
    `);

    row.find("th").attr("title", res[0]);
    row.find("input").val(res[1]);
    row.find("button").on("click", () => {
      addChange(index);
    });
    table.append(row);
  });

  updateAdditionPagination(dbInterface.getPages(lang, query), page);
}

function updateAdditionPagination(pages, selectedPage) {
  const pagination = $("#editChangePagination");
  const page = `
    <li class="page-item">
        <a class="page-link">3</a>
    </li>
    `;

  pagination.html("");

  let startPage = selectedPage - 5;
  if (startPage <= 0) {
    startPage = 1;
  }

  let length = 11;

  if (startPage + length > pages) {
    length = pages - startPage;
  }

  for (let i = startPage; i < startPage + length; i++) {
    const currentPage = $(page);
    const a = currentPage.children("a");
    a.text(i);
    a.on("click", () => {
      updateAdditionTable(i - 1);
    });

    if (i - 1 == selectedPage) {
      currentPage.addClass("active");
    }

    pagination.append(currentPage);
  }
}

function addChange(row) {
  const lang = $("#editChangeLangSelect").find(":selected").text();
  const id = $(`#row-${row}`).find("th").text();
  const value = $(`#row-${row}`).find("input").val();

  console.log(`Adding change of field ${id} to ${value} for language ${lang}`);

  dbInterface.addChange(lang, id, value);

  updatePendingChanges();
}

function updatePendingChanges() {
  $("#pendingChanges").text(dbInterface.getChangeCount());
}
// END MAIN BLOCK
