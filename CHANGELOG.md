# Changelog

## 1.20.0 (08/03/2022)

#### 🚀 Enhancements:

- add semitransparency_experimental flag to API [#108](https://github.com/remove-bg/kaleido-removebg/pull/108)

#### 🐞 Bugfixes:

- Instantiate PubSub Client on server start instead of every request [#109](https://github.com/remove-bg/kaleido-removebg/pull/109)
- Fix CI pipeline [#110](https://github.com/remove-bg/kaleido-removebg/pull/110)

#### 🚨 Security

- Fix url-parse critical vulnerability issue [#111](https://github.com/remove-bg/kaleido-removebg/pull/111)

#### 🔀 Dependencies

- Bump node-fetch from 2.6.1 to 2.6.7 [#113](https://github.com/remove-bg/kaleido-removebg/pull/113)
- Bump node-fetch from 2.6.0 to 2.6.7 in /api [#112](https://github.com/remove-bg/kaleido-removebg/pull/112)
- [js] Update all Yarn dependencies (2022-02-23) [#103](https://github.com/remove-bg/kaleido-removebg/pull/103) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.20.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.20.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.20.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.20.0-cc86`
---

## 1.19.0 (28/02/2022)

#### 🚀 Enhancements:

- Update model version #trivial [#107](https://github.com/remove-bg/kaleido-removebg/pull/107) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.19.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.19.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.19.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.19.0-cc86`
---

## 1.18.0 (16/02/2022)

#### 🚀 Enhancements:

- Improve request logging + Pub/Sub reporting [#51](https://github.com/remove-bg/kaleido-removebg/pull/51) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.18.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.18.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.18.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.18.0-cc86`
---

## 1.17.0 (14/02/2022)

#### 🚀 Enhancements:

- Update model version #trivial [#101](https://github.com/remove-bg/kaleido-removebg/pull/101)

#### 🔀 Dependencies

- [js] Update all Yarn dependencies (2022-02-09) [#99](https://github.com/remove-bg/kaleido-removebg/pull/99)
- [api] Update all Yarn dependencies (2022-02-09) [#100](https://github.com/remove-bg/kaleido-removebg/pull/100)
- [api] Upgrade Node.js to 14.19.0 [#97](https://github.com/remove-bg/kaleido-removebg/pull/97)
- [js] Upgrade Node.js to 14.19.0 [#96](https://github.com/remove-bg/kaleido-removebg/pull/96) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.17.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.17.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.17.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.17.0-cc86`
---

## 1.16.1 (08/02/2022)

#### 🐞 Bugfixes:

- Fix misuse of roi parameter for trimap. #yolo [#98](https://github.com/remove-bg/kaleido-removebg/pull/98) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.16.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.1-cc86`
---

## 1.16.0 (31/01/2022)

#### 🚀 Enhancements:

- Reduce cost of QI trainings [#95](https://github.com/remove-bg/kaleido-removebg/pull/95)
- Add option for inference on CPU [#92](https://github.com/remove-bg/kaleido-removebg/pull/92)
- Architecture change to tackle Preview Vs. Full Resolution discrepancies [#91](https://github.com/remove-bg/kaleido-removebg/pull/91)

#### 🔀 Dependencies

- [js] Update all Yarn dependencies (2022-01-26) [#93](https://github.com/remove-bg/kaleido-removebg/pull/93)
- [api] Update all Yarn dependencies (2022-01-26) [#94](https://github.com/remove-bg/kaleido-removebg/pull/94)
- [api] Upgrade Node.js to 14.18.3 [#90](https://github.com/remove-bg/kaleido-removebg/pull/90)
- [js] Upgrade Node.js to 14.18.3 [#89](https://github.com/remove-bg/kaleido-removebg/pull/89) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.16.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.16.0-cc86`
---

## 1.15.0 (04/01/2022)

#### 🚀 Enhancements:

- Update trimap model with version 1.16.0 #trivial [#88](https://github.com/remove-bg/kaleido-removebg/pull/88)

#### 🔀 Dependencies

- [js] Update all Yarn dependencies (2021-12-29) [#86](https://github.com/remove-bg/kaleido-removebg/pull/86)
- [api] Update all Yarn dependencies (2021-12-29) [#87](https://github.com/remove-bg/kaleido-removebg/pull/87) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.15.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.15.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.15.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.15.0-cc86`
---

## 1.14.1 (20/12/2021)

#### 🐞 Bugfixes:

- Revert "Moved cpu processing into pre and postprocessing" [#85](https://github.com/remove-bg/kaleido-removebg/pull/85) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.14.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.1-cc86`
---

## 1.14.0 (14/12/2021)

#### 🚀 Enhancements:

- Update kaleido-models to version 1.13.0 #trivial [#84](https://github.com/remove-bg/kaleido-removebg/pull/84)
- Moved cpu processing into pre and postprocessing [#83](https://github.com/remove-bg/kaleido-removebg/pull/83) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.14.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.14.0-cc86`
---

## 1.13.0 (06/12/2021)
*No changelog for this release.* 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.13.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.13.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.13.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.13.0-cc86`
---

## 1.12.0 (03/12/2021)

#### 🚀 Enhancements:

- Added support to configure number of core workers [#82](https://github.com/remove-bg/kaleido-removebg/pull/82)
- Expose foreground coordinates in json response and http headers [#76](https://github.com/remove-bg/kaleido-removebg/pull/76)
- Expose custom headers to frontend clients [#75](https://github.com/remove-bg/kaleido-removebg/pull/75)

#### 🔀 Dependencies

- Updated core dependencies [#81](https://github.com/remove-bg/kaleido-removebg/pull/81)
- [js] Upgrade Node.js to 14.18.2 [#79](https://github.com/remove-bg/kaleido-removebg/pull/79)
- [api] Update all Yarn dependencies (2021-12-01) [#78](https://github.com/remove-bg/kaleido-removebg/pull/78)
- [js] Update all Yarn dependencies (2021-12-01) [#77](https://github.com/remove-bg/kaleido-removebg/pull/77)
- [api] Upgrade Node.js to 14.18.2 [#80](https://github.com/remove-bg/kaleido-removebg/pull/80) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.12.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.12.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.12.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.12.0-cc86`
---

## 1.11.1 (25/11/2021)

#### 🚀 Enhancements:

- Try and fix CircleCI build #trivial [#71](https://github.com/remove-bg/kaleido-removebg/pull/71)
- Remove removebg-core as a dependency #trivial [#68](https://github.com/remove-bg/kaleido-removebg/pull/68)

#### 🐞 Bugfixes:

- Update config.yml #trivial [#74](https://github.com/remove-bg/kaleido-removebg/pull/74)
- Update config.yml [#73](https://github.com/remove-bg/kaleido-removebg/pull/73)
- Update config.yml [#72](https://github.com/remove-bg/kaleido-removebg/pull/72)
- Patch pyproject.toml without setuptools_scm #trivial [#70](https://github.com/remove-bg/kaleido-removebg/pull/70)
- Patch CircleCI package installation #trivial [#69](https://github.com/remove-bg/kaleido-removebg/pull/69)
- setup.py strikes back #yolo [#67](https://github.com/remove-bg/kaleido-removebg/pull/67) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.11.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.1-cc86`
---

## 1.11.0 (24/11/2021)

#### 🚀 Enhancements:

- Add foreground coordinates w.r.t. input image in output message [#66](https://github.com/remove-bg/kaleido-removebg/pull/66)
- Make Danger checks lowercase [#63](https://github.com/remove-bg/kaleido-removebg/pull/63)

#### 🐞 Bugfixes:

- Fix assertion [#65](https://github.com/remove-bg/kaleido-removebg/pull/65)

#### 🔀 Dependencies

- [js] Update all Yarn dependencies (2021-11-17) [#64](https://github.com/remove-bg/kaleido-removebg/pull/64) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.11.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.11.0-cc86`
---

## 1.10.0 (16/11/2021)

#### 🚀 Enhancements:

- QI Improvement [#59](https://github.com/remove-bg/kaleido-removebg/pull/59)
- Update kaleido-models.yml [#60](https://github.com/remove-bg/kaleido-removebg/pull/60)
- Smaller docker image [#57](https://github.com/remove-bg/kaleido-removebg/pull/57)
- Torch dependencies with cuda [#58](https://github.com/remove-bg/kaleido-removebg/pull/58)
- Added core server tests [#54](https://github.com/remove-bg/kaleido-removebg/pull/54)
- QI enhancement [#56](https://github.com/remove-bg/kaleido-removebg/pull/56)
- Removed setup.py [#55](https://github.com/remove-bg/kaleido-removebg/pull/55)
- Add verification to Kaleido Models when fetching [#52](https://github.com/remove-bg/kaleido-removebg/pull/52)

#### 🐞 Bugfixes:

- Temporary fix for "Deploy on Gemfury" on CircleCI [#62](https://github.com/remove-bg/kaleido-removebg/pull/62)
- Add --verbose in "Deploy to Gemfury" step to investigate Bad Request error [#61](https://github.com/remove-bg/kaleido-removebg/pull/61) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.10.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.10.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.10.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.10.0-cc86`
---

## 1.9.1 (02/11/2021)

#### 🚀 Enhancements:

- QI release [#53](https://github.com/remove-bg/kaleido-removebg/pull/53) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.9.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.1-cc86`
---

## 1.9.0 (02/11/2021)

#### 🚀 Enhancements:

- Fixed linting errors discovered by flake8 [#45](https://github.com/remove-bg/kaleido-removebg/pull/45)
- Code formatting changes black and isort [#44](https://github.com/remove-bg/kaleido-removebg/pull/44)
- Add script to query Danni for the number of valid Dans at a given date in a specific Batch [#41](https://github.com/remove-bg/kaleido-removebg/pull/41)
- Refactored server code [#43](https://github.com/remove-bg/kaleido-removebg/pull/43)

#### 🚨 Security

- Update kaleido-api to fix critical vulnerability #yolo [#50](https://github.com/remove-bg/kaleido-removebg/pull/50)

#### 🔀 Dependencies

- [js] Update all Yarn dependencies (2021-10-20) [#48](https://github.com/remove-bg/kaleido-removebg/pull/48)
- [api] Upgrade Node.js to 14.18.1 [#47](https://github.com/remove-bg/kaleido-removebg/pull/47)
- [js] Upgrade Node.js to 14.18.1 [#46](https://github.com/remove-bg/kaleido-removebg/pull/46)
- [js] Update all Yarn dependencies (2021-10-06) [#42](https://github.com/remove-bg/kaleido-removebg/pull/42) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.9.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.9.0-cc86`
---

## 1.8.0 (05/10/2021)

#### 🚀 Enhancements:

- Update trimap model and dependencies [#40](https://github.com/remove-bg/kaleido-removebg/pull/40)
- Improve the automatic QI training [#39](https://github.com/remove-bg/kaleido-removebg/pull/39)

#### 🔀 Dependencies

- [api] Upgrade Node.js to 14.18.0 [#38](https://github.com/remove-bg/kaleido-removebg/pull/38)
- [js] Upgrade Node.js to 14.18.0 [#37](https://github.com/remove-bg/kaleido-removebg/pull/37) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.8.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.8.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.8.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.8.0-cc86`
---

## 1.7.0 (29/09/2021)

#### 🚀 Enhancements:

- Added python tooling config [#9](https://github.com/remove-bg/kaleido-removebg/pull/9)
- Refactored image module [#27](https://github.com/remove-bg/kaleido-removebg/pull/27)

#### 🐞 Bugfixes:

- Removed encoding_kwargs PIL.Image.fromarray [#36](https://github.com/remove-bg/kaleido-removebg/pull/36)
- Added missing dpi argument in encoding [#35](https://github.com/remove-bg/kaleido-removebg/pull/35)
- Fix PIL not handling jpg but only jpeg [#34](https://github.com/remove-bg/kaleido-removebg/pull/34)
- Assertion fix in _validate_crop() [#33](https://github.com/remove-bg/kaleido-removebg/pull/33)
- Lower/upper str before assertion [#32](https://github.com/remove-bg/kaleido-removebg/pull/32)
- Fix BestCheckpointNameFixer for QI training [#29](https://github.com/remove-bg/kaleido-removebg/pull/29)

#### 🔀 Dependencies

- Update dependency to shadowgen-core [#31](https://github.com/remove-bg/kaleido-removebg/pull/31)
- [api] Update all Yarn dependencies (2021-09-22) [#30](https://github.com/remove-bg/kaleido-removebg/pull/30) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.7.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.7.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.7.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.7.0-cc86`
---

## 1.6.2 (17/09/2021)

#### 🐞 Bugfixes:

- Disable nudging for old ps plugin [#28](https://github.com/remove-bg/kaleido-removebg/pull/28) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.6.2`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.2-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.2-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.2-cc86`
---

## 1.6.1 (16/09/2021)
*No changelog for this release.* 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.6.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.1-cc86`
---

## 1.6.0 (10/09/2021)

#### 🚀 Enhancements:

- Update kaleido-models version [#25](https://github.com/remove-bg/kaleido-removebg/pull/25)
- Refactored server code [#6](https://github.com/remove-bg/kaleido-removebg/pull/6)

#### 🐞 Bugfixes:

- Refactor exif test: Recreate images with compression level=100 [#26](https://github.com/remove-bg/kaleido-removebg/pull/26)
- Revert "Refactored server code" [#24](https://github.com/remove-bg/kaleido-removebg/pull/24)
- Fix dpi test [#20](https://github.com/remove-bg/kaleido-removebg/pull/20) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.6.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.6.0-cc86`
---

## 1.5.0 (09/09/2021)

#### 🚀 Enhancements:

- [BGR-28] Canva ECR Docker push [#23](https://github.com/remove-bg/kaleido-removebg/pull/23)

#### 🔀 Dependencies

- [api] Update all Yarn dependencies (2021-09-08) [#22](https://github.com/remove-bg/kaleido-removebg/pull/22)
- [js] Update all Yarn dependencies (2021-09-08) [#21](https://github.com/remove-bg/kaleido-removebg/pull/21) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.5.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.5.0-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.5.0-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.5.0-cc86`
---

## 1.4.2 (07/09/2021)

#### 🚀 Enhancements:

- Prepare the nudging message for PS plugins < 2.*.* [#2](https://github.com/remove-bg/kaleido-removebg/pull/2)

#### 🚨 Security

- 🚨 [security] [api] Update express-fileupload: 1.1.5 → 1.1.10 (patch) [#19](https://github.com/remove-bg/kaleido-removebg/pull/19)

#### 🔀 Dependencies

- [api] Upgrade Node.js to 14.17.6 [#18](https://github.com/remove-bg/kaleido-removebg/pull/18)
- [js] Upgrade Node.js to 14.17.6 [#17](https://github.com/remove-bg/kaleido-removebg/pull/17)
- 🚨 [security] [api] Update ws: 7.2.1 → 7.5.4 (minor) [#15](https://github.com/remove-bg/kaleido-removebg/pull/15) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.4.2`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.2-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.2-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.2-cc86`
---

## 1.4.1 (07/09/2021)
*No changelog for this release.* 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.4.1`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.1-cc75`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.1-cc61`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.1-cc86`
---

## 1.4.0 (07/09/2021)

#### 🚀 Enhancements:

- Changed update-requirements.sh to exclude torch dependencies as already included in base image [#10](https://github.com/remove-bg/kaleido-removebg/pull/10)

#### 🔧 Changes:

- Automated QI Training [#8](https://github.com/remove-bg/kaleido-removebg/pull/8) 

### Docker Images

* `eu.gcr.io/removebg-226919/removebg-api:1.4.0`
* `eu.gcr.io/removebg-226919/removebg-core:1.4.0-cc75`
---

## v1.3.0 (23/08/2021)
Dependency refactoring