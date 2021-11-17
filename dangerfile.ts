/**
 * BEFORE EDITING THIS FILE, PLEASE READ http://danger.systems/js/usage/culture.html
 *
 * This file is split into three parts:
 * 1) Rules that require or suggest changes to the code, the PR, etc.
 * 2) Rules that celebrate achievements
 * 3) Automations that perform actions on the PR
 */
import { danger, fail, message, schedule, warn, markdown } from 'danger'
import todos from 'danger-plugin-todos'
import { commonValidJson, jsConsoleCommands, jsTestShortcuts } from 'danger-plugin-toolbox'
import * as fs from 'fs';

// Check if PR is opened by @depfu
const isDepfuPR = danger.github.pr.user.login == 'depfu[bot]' && danger.github.pr.user.type == 'Bot'

// Check if it's a trivial PR
const declaredTrivial = danger.github.pr.title.toLowerCase().includes("#trivial") || danger.github.pr.title.toLowerCase().includes("#yolo")

// Get stats
const { additions = 0, deletions = 0 } = danger.github.pr

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~ Required or suggested changes                                          ~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/**
 * Rule: PR should have some changes
 * Reason: If these are all empty something has gone wrong,
 *         better to raise it in a comment
 */
if (danger.git.modified_files.length == 0 && danger.git.created_files.length == 0 && danger.git.deleted_files.length == 0) {
  fail("😱 This Pull Request has no changes at all, this is likely an issue during development.")
}

/**
 * Rule: Exactly 1 reviewer is required.
 * Reason: No reviewer tends to leave a PR in a state where nobody is
 *         responsible. Similarly, more than 1 reviewer doesn't clearly state
 *         who is responsible for the review.
 */
const reviewersCount = danger.github.requested_reviewers.users.length
if (reviewersCount === 0 && !isDepfuPR) {
  warn(`🕵 Please assign someone to review this PR.`)
} else if (reviewersCount > 1) {
  warn(`🤔 It's great to have ${reviewersCount} reviewers, but more than 1 reviewer may lead to uncertainty as to who is responsible for the review.`)
}

/**
 * Rule: Always ensure we assign someone
 * Reason: An assignee is helpful, so that our Slackbot can do its work correctly
 */
//
if (danger.github.pr.assignee === null) {
  warn(":point_up: Please assign someone (probably yourself?) to merge this PR")
}

/**
 * Rule: Warn if PR has more than 500 changed lines
 * Reason: Big Pull Requests are harder to review.
 */
var bigPRThreshold = 500;
if (danger.github.pr.additions + danger.github.pr.deletions > bigPRThreshold && !isDepfuPR) {
  warn(':exclamation: Big PR');
  message('Consider splitting this relatively large Pull Request into smaller PRs to ensure faster, easier reviews.', { icon: '⛰' });
}

/**
 * Rule: Ensure the PR body contains a link to the Notion card.
 * Reason: It's the most efficient way to jump from Github to Notion to update the
 *         ticket.
 */
const prBody = String(danger.github.pr.body)
const ticketUrlPattern = /https:\/\/www\.notion\.so\/kaleidoai\/(.+)/g
if (!ticketUrlPattern.test(prBody) && !(isDepfuPR || declaredTrivial)) {
  message(`I can't find a Notion card URL in the PR description.`, { icon: '🔍' })
}

/**
 * Rule: Require a PR summary
 * Reason: Mainly to encourage writing up some reasoning about the PR,
 *         rather than just leaving a title
 */
if (prBody.length < 5 && !(isDepfuPR || declaredTrivial)) {
  fail(":writing_hand: Please provide a summary in the Pull Request description")
}

/**
 * Rule: Only allow PRs against main
 * Reason: Pull requests against other branches are probably a mistake
 */
if (danger.github.pr.base.ref != "main") {
  fail(`👨‍💻 Please re-submit this Pull Request against the <samp>main</samp> branch, instead of <samp>${danger.github.pr.base.ref}</samp>!`)
}

/**
 * Rule: PR needs to have a label
 * Reason: Labels are used to categorize the PR into a group which
 *         is used in the Changelog.
 */
 if (danger.github.issue.labels.length == 0) {
  fail("🏷 Please categorize your PR by adding a label!")
} else if (danger.github.issue.labels.length > 1 && !isDepfuPR) {
  fail(`🏷 Please use exactly one label for your PR, instead of ${danger.github.issue.labels.length}!`)
}

/**
 * Rule: Check for TODO's in app code
 * Reason: It's bad form to leave TODO or FIXME in the code
 */
schedule(todos({
  keywords: ['TODO', 'FIXME', '@TODO']
}))

/**
 * Rule: JSON files need to be valid
 * Reason: Invalid JSON files can break builds or the app
 */
commonValidJson({ logType: 'fail' })

/**
 * Rule: Check for skipped or focused tests
 * Reason: Warns for skipped tests and fails for focused tests, because
 *         this prevents the whole test suite from running.
 */
 jsTestShortcuts({ logTypeSkipped: 'warn', logTypeFocused: 'fail' });

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~ Achievements                                                            ~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/**
 * Rule: Show some stats
 * Reason: Stats are fun
 */
message(`This Pull Request added 🟩 <b>${additions}</b> and removed 🟥 <b>${deletions}</b> lines.`, { icon: ':octocat:' })

/**
 * Rule: Celebrate PRs that remove more code than they add.
 * Reason: Less is more!
 */
if (danger.github.pr.deletions > danger.github.pr.additions && !isDepfuPR) {
  message(`Thanks for keeping the project lean!`, { icon: '👏' })
}

/**
 * Rule: Mark pull requests opened by Depfu
 * Reason: Make it easy to see what is an automated PR
 */
if (isDepfuPR) {
  message("This is an automated Pull Request opened by <a href=\"https://depfu.com\">depfu</a>!", { icon: '🤖' })
}

/**
 * Rule: Mark pull requests that were declared trivial
 * Reason: Make it easy to see if a PR was declared trivial
 */
if (declaredTrivial && !isDepfuPR) {
  message("This Pull Request was marked <samp>#trivial</samp>!", { icon: '✨' })
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* ~ Automations                                                            ~ */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/**
 * Rule: Approve Depfu and Trivial PRs
 */
if (isDepfuPR || declaredTrivial) {
  danger.github.api.pulls.createReview({
    owner:       danger.github.thisPR.owner,
    repo:        danger.github.thisPR.repo,
    pull_number: danger.github.thisPR.number,
    body: "CI automatically approved this pull request! :white_check_mark: ",
    event: 'APPROVE'
  })
}

// ---------------------------------------------------------------------------------------------------------------

/**
 * Rule: Run yarn audit
 */
const yarnAuditAPI = JSON.parse(require('child_process').execSync(`yarn audit --summary --json --non-interactive --no-progress --group dependencies || exit 0`, {cwd: 'api'}).toString());
const vulnerabilitiesAPI = Object.values(yarnAuditAPI.data.vulnerabilities).reduce(
  (t, n) => Number(t) + Number(n),
);

var vulnerabilityStringAPI = '';
Object.keys(yarnAuditAPI.data.vulnerabilities).forEach(key => {
  if (yarnAuditAPI.data.vulnerabilities[key] > 0) {
    vulnerabilityStringAPI = vulnerabilityStringAPI + `${yarnAuditAPI.data.vulnerabilities[key]} ${key}, `;
  }
});
vulnerabilityStringAPI = '(' + vulnerabilityStringAPI.slice(0, -2) + ')';

if (vulnerabilitiesAPI == 0) {
  message(`Found <b>0</b> vulnerabilities in <b>${yarnAuditAPI.data.totalDependencies}</b> scanned <b>api</b> packages`, { icon: '⛑' } );
} else if (yarnAuditAPI.data.vulnerabilities.critical > 0) {
  fail(`🚨 Found <b>${yarnAuditAPI.data.vulnerabilities.critical}</b> critical vulnerabilities in <b>${yarnAuditAPI.data.totalDependencies}</b> scanned <b>api</b> packages ${vulnerabilityStringAPI}`);
} else {
  warn(`🔥 Found <b>${vulnerabilitiesAPI}</b> vulnerabilities in <b>${yarnAuditAPI.data.totalDependencies}</b> scanned <b>api</b> packages ${vulnerabilityStringAPI}`);
}

/**
 * Rule: Analyze linter files
 */
var yamllintResult = fs.readFileSync("lint/yamllint.txt").toString();
if (yamllintResult.includes("[error]") || yamllintResult.includes("[warning]")) {
  const yamllintRegex = /^([^:]+):(\d+):(\d+): \[(\w+)\] (.+) \(([\w_\-\.]+)\)/gmi
  yamllintResult = yamllintResult.replace(yamllintRegex, '| `$1` | $2 | $3 | **$4** | `$6` | $5 |')

  const markdownHeaderYamllint = "| File  | Line | Position | Level | Module | Message |\n| ----- |:----:|:--------:|:-----:|:------:| ------- |\n"
  markdown("### YAML Lint\n\n" + markdownHeaderYamllint + yamllintResult)
}

if (yamllintResult.includes("warning") || yamllintResult.includes("error")) {
  fail("📎 There are issues in your `.yaml` files!")
}

var kubevalJson = JSON.parse(fs.readFileSync("lint/kubeval.json").toString());
var kubevalResult = '';
const markdownHeaderKubeval = "| File  | Status | Kind     | Errors |\n| ----- |:------:| -------- | ------ |\n"

kubevalJson.forEach(obj => {
  var errors = "";
  obj.errors.forEach(error => {
    errors += "<li>" + error + "</li>";
  });
  kubevalResult += "| `" + obj.filename + "` | **" + obj.status + "** | `" + obj.kind + "` | " + errors + " |\n";
});

markdown("### Kubernetes Configuration\n\n" + markdownHeaderKubeval + kubevalResult);

if (kubevalResult.includes("invalid")) {
  fail("`☸️ Invalid Kubernetes configuration found!")
}
