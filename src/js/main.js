// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap';
import $ from "jquery";
import Papa from 'papaparse';

let gameFiles = {};
let langFiles = {};

// SETUP BLOCK

$(document).ready(() => {
    $(folderPicker).on('click', function() {
        window.showDirectoryPicker({
            id: 'wtDir', 
            mode: 'readwrite'
        }).then(function(directory) {
            verifyDirectory(directory);
        });
    });
    
    $(updateConfigButton).on('click', function() {
        gameFiles['config.blk'].getFile().then(file => {
            file.text().then(content => {
                // Update the configuration file
                let newContent;
                const debugRegex = /debug\s*\{[^{}]*\}/;
                if (debugRegex.test(content)) {
                    newContent = content.replace(debugRegex, match => {
                        return match.includes('testLocalization:b=yes') ? match : match.replace(/\}$/, '  testLocalization:b=yes\n}');
                    });
                } else {
                    newContent = content + '\ndebug {\n    testLocalization:b=yes\n}';
                }
    
                // Write the new content to the configuration file
                gameFiles['config.blk'].createWritable().then(writable => {
                    writable.write(newContent).then(() => {
                        writable.close();
                        setTimeout(async () => {
                            verifyConfiguration(await gameFiles['config.blk'].getFile());
                        }, 500);
                    });
                });
            });
        });
    });
    
    $(checkFilesButton).on('click', verifyLangFolderExists);
});

// END SETUP BLOCK

// CONFIG BLOCK

function verifyDirectory(directory) {
    var entries = {};

    Array.fromAsync(directory.entries(), element => entries[element[0]] = element[1]).then(() => {
        if (entries['config.blk'] != undefined) {
            gameFiles = entries;

            // Success, show the next step
            $('#locateGameHeader .spinner-border').attr('hidden', true);
            $('#locateGameHeader .bi-check-lg').attr('hidden', false);
            $('#locateGameHeader .bi-x-lg').attr('hidden', true);
            $('#wrongGamePath').attr('hidden', true);
            $('#locateGameCollapse input').attr('value', directory.name);

            setTimeout(async () => {
                $('#checkConfigHeader > button').attr('disabled', false);
                $('#checkConfigHeader > button').trigger('click');
                $('#checkConfigHeader > button').attr('disabled', true);
                $('#checkConfigHeader .spinner-border').attr('hidden', false);

                verifyConfiguration(await entries['config.blk'].getFile());
            }, 500)
        } else {
            // Failure, show the error message
            $('#locateGameHeader .spinner-border').attr('hidden', true);
            $('#locateGameHeader .bi-check-lg').attr('hidden', true);
            $('#locateGameHeader .bi-x-lg').attr('hidden', false);
            $('#wrongGamePath').attr('hidden', false);
        }
    });
}

function verifyConfiguration(configFile) {
    configFile.text().then(content => {
        const regex = /debug\s*\{[^{}]*\btestLocalization:b=yes\b[^{}]*\}/;
        if (regex.test(content)) {
            // Success, show the next step
            $('#checkConfigHeader .spinner-border').attr('hidden', true);
            $('#checkConfigHeader .bi-check-lg').attr('hidden', false);
            $('#checkConfigHeader .bi-x-lg').attr('hidden', true);
            $('#checkConfigText').attr('hidden', true);
            $('#checkConfigTextSuccess').attr('hidden', false);
            $('#checkConfigTextFail').attr('hidden', true);

            setTimeout(async () => {
                $('#checkFilesHeader > button').attr('disabled', false);
                $('#checkFilesHeader > button').trigger('click');
                $('#checkFilesHeader > button').attr('disabled', true);
                $('#checkFilesHeader .spinner-border').attr('hidden', false);

                verifyLangFolderExists();
            }, 500);
        } else {
            // Failure, prompt the user to fix the configuration file
            $('#checkConfigHeader .spinner-border').attr('hidden', true);
            $('#checkConfigHeader .bi-check-lg').attr('hidden', true);
            $('#checkConfigHeader .bi-x-lg').attr('hidden', false);
            $('#checkConfigText').attr('hidden', true);
            $('#checkConfigTextSuccess').attr('hidden', true);
            $('#checkConfigTextFail').attr('hidden', false);
        }
    });
}

function verifyLangFolderExists() {
    if (gameFiles['lang']?.kind == 'directory') {
            // Success, show the next step
            $('#checkFilesHeader .spinner-border').attr('hidden', true);
            $('#checkFilesHeader .bi-check-lg').attr('hidden', false);
            $('#checkFilesHeader .bi-x-lg').attr('hidden', true);
            $('#checkFilesText').attr('hidden', true);
            $('#checkFilesTextSuccess').attr('hidden', false);
            $('#checkFilesTextFail').attr('hidden', true);

            setTimeout(async () => {
                $('#configWindow').attr('style', 'transition-duration: .75s; top: -105vh');

                const files = await Array.fromAsync(await gameFiles['lang'].values());
                const tasks = files.map(async entry => {
                    return openCSV(await entry.getFile());
                });
                
                Promise.all(tasks).then(() => {
                    console.log("ALL FILES LOADED!");
                    bootstrap.Toast.getOrCreateInstance($('#filesLoadedToast'), {
                        autohide: true,
                        delay: 3000
                    }).show();
                });
                
            }, 500);
    } else {
        // Failure, prompt the user to start the game
        $('#checkFilesHeader .spinner-border').attr('hidden', true);
        $('#checkFilesHeader .bi-check-lg').attr('hidden', true);
        $('#checkFilesHeader .bi-x-lg').attr('hidden', false);
        $('#checkFilesText').attr('hidden', true);
        $('#checkFilesTextSuccess').attr('hidden', true);
        $('#checkFilesTextFail').attr('hidden', false);
    }
}

// END CONFIG BLOCK

// MAIN BLOCK

function openCSV(file) {
    return new Promise((resolve) => {
        Papa.parse(file, {
            header: true,
            complete: function(results) {
                console.log("Loaded " + file.name + " with " + results.data.length + " rows");
                langFiles[file.name] = results;

                resolve();
            }
        });
    });
}