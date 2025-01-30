// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap'
import $ from "jquery";

let gameFiles = {};

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
                $('#locateGameHeader > button').attr('disabled', true);
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