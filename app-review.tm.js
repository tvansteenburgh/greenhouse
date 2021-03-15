// ==UserScript==
// @name         Greenhouse App Review
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Add shortcut buttons to resume review screen
// @author       Tim Van Steenburgh
// @match        https://canonical.greenhouse.io/application_review*
// @require      https://cdnjs.cloudflare.com/ajax/libs/arrive/2.4.1/arrive.min.js
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    var doSubmit = true;
    makeAction('Lacking Skills', 'Lacking skill(s)/qualification(s)', '', 'Candidate rejection - application stage', doSubmit);
    makeAction('No Cover Letter', 'Other (add notes below)', 'No cover letter', 'Candidate rejection - application stage', doSubmit);
    makeAction('Wrong Timezone', 'Wrong geography', '', 'Candidate rejection - application stage', doSubmit);
    makeAction('Wrong Job', 'Other (add notes below)', 'Cover letter is for a different job/company', 'Candidate rejection - application stage', doSubmit);
    makeAction('Illegible', 'Other (add notes below)', 'Submission not in English', 'Candidate rejection - application stage', doSubmit);

    function makeAction(btnText, reasonOption, notes, templateOption, doSubmit) {
        var arriveOptions = {
            fireOnAttributesModification: true,
            onceOnly: true,
            existing: true
        };
        var node = document.createElement ('div');
        node.innerHTML = '<button type="button" class="customAction">' + btnText + '</button>';
        node.addEventListener (
            "click",
            function(event) {
                document.getElementById('reject_button').click();
                document.arrive(
                    "#rejection_reason",
                    arriveOptions,
                    function() {
                        var sel = $(this);
                        sel[0].selectedIndex = [...sel[0].options].findIndex (option => option.text === reasonOption);
                        sel.trigger("liszt:updated");
                        document.getElementById('rejection_reason_note').value = notes;

                        sel = $('#rejection_template_chooser');
                        sel[0].selectedIndex = [...sel[0].options].findIndex (option => option.text === templateOption);
                        sel.trigger("liszt:updated");

                        if (doSubmit) {
                            document.arrive(
                                '#reject_with_email_button:not([disabled])',
                                arriveOptions,
                                function() {
                                    $(this).click();
                                    Arrive.unbindAllArrive();
                                },
                            );
                        }
                    },
                );
            },
            false
        );
        document.getElementById('actions').appendChild (node);
    }

    GM_addStyle(".customAction { background-color: white; padding: 1em 0; margin: .5em 0; font-weight: bold; width: 230px; cursor: pointer; }");
})();
