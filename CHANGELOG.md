# Changelog

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