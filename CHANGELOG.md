# Changelog

<!--next-version-placeholder-->

## v3.5.0 (2024-01-18)

### Feature

* Add verification of the packet id ([#105](https://github.com/Bluetooth-Devices/bthome-ble/issues/105)) ([`c428f92`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c428f927b8dbc4f02ef006c15932aca5fa74877f))

## v3.4.2 (2024-01-17)

### Fix

* Fix counter verification ([#104](https://github.com/Bluetooth-Devices/bthome-ble/issues/104)) ([`dead672`](https://github.com/Bluetooth-Devices/bthome-ble/commit/dead67297a2a5662d6a9b12fcc8e671ae1d833a1))

## v3.4.1 (2024-01-10)

### Fix

* Use volume storage instead of water storage ([#102](https://github.com/Bluetooth-Devices/bthome-ble/issues/102)) ([`4cf20bf`](https://github.com/Bluetooth-Devices/bthome-ble/commit/4cf20bfd027286ba7ca842125d3cafbc0797e6c1))

## v3.4.0 (2024-01-10)

### Feature

* Add water storage sensor ([#101](https://github.com/Bluetooth-Devices/bthome-ble/issues/101)) ([`6eb80e0`](https://github.com/Bluetooth-Devices/bthome-ble/commit/6eb80e0e120f7c8ef6ce4b7ee5057ae5356192b3))

## v3.3.1 (2023-12-15)

### Fix

* No check of encryption counter when bindkey has not been verified ([#97](https://github.com/Bluetooth-Devices/bthome-ble/issues/97)) ([`43f1412`](https://github.com/Bluetooth-Devices/bthome-ble/commit/43f14123b68732f41552d2f198dbbf2323763614))

## v3.3.0 (2023-12-13)

### Feature

* Add check for increasing encryption counter ([#92](https://github.com/Bluetooth-Devices/bthome-ble/issues/92)) ([`a58cf7b`](https://github.com/Bluetooth-Devices/bthome-ble/commit/a58cf7bf84bacaf0b8436f03499710d5b83e3add))

## v3.2.0 (2023-10-01)

### Feature

* Add raw hex sensor ([#91](https://github.com/Bluetooth-Devices/bthome-ble/issues/91)) ([`6f9969e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/6f9969e73efe0ccaa810d3e7aa136af673eca3c2))

## v3.1.1 (2023-08-20)

### Fix

* Replace datetime.utcfromtimestamp ([#87](https://github.com/Bluetooth-Devices/bthome-ble/issues/87)) ([`0184fe7`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0184fe7b04caabc45fe3e8da1191269a7d19b975))

## v3.1.0 (2023-08-13)

### Feature

* Add text sensor ([#86](https://github.com/Bluetooth-Devices/bthome-ble/issues/86)) ([`2bfcd9b`](https://github.com/Bluetooth-Devices/bthome-ble/commit/2bfcd9b9b4a2321eb229298258235b61a97ae9d2))

## v3.0.0 (2023-07-15)

### Feature

* Add ability to set the bind key after init ([#83](https://github.com/Bluetooth-Devices/bthome-ble/issues/83)) ([`1826139`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1826139cc81bbdb0b9fdd616b16fa92b07654f6b))

### Breaking

* the bindkey should no longer be set directly on the object, call `set_bindkey` instead ([`1826139`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1826139cc81bbdb0b9fdd616b16fa92b07654f6b))

## v2.13.0 (2023-07-15)

### Feature

* Switch from pycryptodomex to cryptography ([`0cdc8e6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0cdc8e674bc5f6d6f8cef64891d30c1e90f415ae))

### Fix

* Lint ([`576342d`](https://github.com/Bluetooth-Devices/bthome-ble/commit/576342d480f7a2f01337e96141dc4db2d896a82e))

## v2.12.2 (2023-07-15)

### Fix

* Decryption bug fixed ([`dfb12e6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/dfb12e6d46e29cadaff39b5e9d6625a708502d05))

## v2.12.1 (2023-07-07)

### Fix

* Bump sensor-state-data to 2.16.1 ([`9657a91`](https://github.com/Bluetooth-Devices/bthome-ble/commit/9657a91bd39550b74fe3d822c1e47b407aa25131))
* Fix for repeated events ([`285da3c`](https://github.com/Bluetooth-Devices/bthome-ble/commit/285da3c76e719043295225f81b9c96279ea7554c))

## v2.12.0 (2023-06-18)

### Feature

* Timestamp acceleration and gyroscope ([`07c6b40`](https://github.com/Bluetooth-Devices/bthome-ble/commit/07c6b4023dd3e960ab16bb80a5565f91738b55ad))

### Fix

* Bump semantic release ([`ebe3484`](https://github.com/Bluetooth-Devices/bthome-ble/commit/ebe34848db5d3a88ac2023cb26bf2803e51b88fd))
* Fix failing tests ([`3cf0634`](https://github.com/Bluetooth-Devices/bthome-ble/commit/3cf0634cf2eb91b55990746f161d9605e00d0fde))
* Use utcfromtimestamp ([`1fea0eb`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1fea0eb3a257c5c4e8070fa40ee221a5a297ef86))

## v2.11.3 (2023-05-19)
### Fix
* Revert trigger based device name ([`f2b5303`](https://github.com/Bluetooth-Devices/bthome-ble/commit/f2b5303952d5e4ec1ac63307ba43aca7c9262a36))

## v2.11.2 (2023-05-12)
### Fix
* Pre-commit bump and bump release ([`97540cc`](https://github.com/Bluetooth-Devices/bthome-ble/commit/97540cccf52e6c49357082917228a1b704579ba0))

## v2.11.1 (2023-05-12)
### Fix
* Add trigger based device to device type ([`0d0076b`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0d0076ba6ee54fd1d68a67453c549f27fc9e5a2d))

## v2.11.0 (2023-05-04)
### Feature
* Add sleepy device bit ([`d61e63e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d61e63ebd68461fae26ef08b05c5d5771dae45fb))

### Fix
* Clean code ([`26bc5d2`](https://github.com/Bluetooth-Devices/bthome-ble/commit/26bc5d2ebd2e840c2a32b140275c8eee7c2f79e8))

## v2.10.1 (2023-04-28)
### Fix
* Add sleepy sensors to init ([`7a82a50`](https://github.com/Bluetooth-Devices/bthome-ble/commit/7a82a50f2be23e3c429626fc98f03a6ab80ed7bb))

## v2.10.0 (2023-04-28)
### Feature
* Add sleepy devices ([`2bcbf38`](https://github.com/Bluetooth-Devices/bthome-ble/commit/2bcbf38e51bb6d1a0791682acceacb721edfc866))

### Fix
* Typo ([`7ddb135`](https://github.com/Bluetooth-Devices/bthome-ble/commit/7ddb1357421e9f419529955e05cb98915539aeab))

## v2.9.0 (2023-03-12)
### Feature
* Add water sensor ([`c228d77`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c228d772a4c2757e59697b9b233057d1648f9525))

## v2.8.0 (2023-03-05)
### Feature
* Add gas water energy meter ([`152bcea`](https://github.com/Bluetooth-Devices/bthome-ble/commit/152bcea19394fa32b82fca1d2cfffcba5609d81c))

## v2.7.0 (2023-02-25)
### Feature
* Add gas sensor ([`956610f`](https://github.com/Bluetooth-Devices/bthome-ble/commit/956610fd72e5490f0dbf47ab5cbac7871c8d2565))

## v2.6.0 (2023-02-17)
### Feature
* Add possibility to include mac in payload ([`1059aa1`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1059aa1eca2fc7ac7518e0a9dbbb822548417bf0))

### Fix
* Fix flake 8 line length error ([`e7490b4`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e7490b487201abf74c6e7271cee1d9eab1db2c2c))

## v2.5.2 (2023-02-10)
### Fix
* Parse objects of the same time correctly ([#47](https://github.com/Bluetooth-Devices/bthome-ble/issues/47)) ([`27e5982`](https://github.com/Bluetooth-Devices/bthome-ble/commit/27e5982214ee34cca6243532dff4e9b2e65e0da9))

## v2.5.1 (2023-01-24)
### Fix
* Correct data length check ([`aed08c4`](https://github.com/Bluetooth-Devices/bthome-ble/commit/aed08c4d07a7fc1dd25d5f081a88d88171946498))

## v2.5.0 (2023-01-11)
### Feature
* Add voltage with 1 digit ([`acd1da7`](https://github.com/Bluetooth-Devices/bthome-ble/commit/acd1da7e62a652cba588d8b543479afd6b86a42f))

## v2.4.1 (2023-01-04)
### Fix
* Bump sensor-state-data ([`1202ace`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1202ace26e0a5acdb26cc90e4eae1d8deab3a2dd))
* Bump sensor-state-data ([`7bff7be`](https://github.com/Bluetooth-Devices/bthome-ble/commit/7bff7be46ad1c0ca082c7801f7741343c92cb342))
* Bump sensor-state-data ([`930b222`](https://github.com/Bluetooth-Devices/bthome-ble/commit/930b22299e20c61bd8256b4a9db3b4306e4a224a))

## v2.4.0 (2022-12-17)
### Feature
* Add volume and packet id ([`aaefa4e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/aaefa4e5913bc6db80ad98e4e2947fb58e8abb83))

### Fix
* Update tests and dependencies ([`bb9d0a2`](https://github.com/Bluetooth-Devices/bthome-ble/commit/bb9d0a2c4941915dd9e37b8fe8db3ef5f8c627d3))

## v2.3.1 (2022-11-19)
### Fix
* Warning for numerical order object id ([`b86feaa`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b86feaa7f2845c1471bd13d48443a23122078bc6))

## v2.3.0 (2022-11-18)
### Feature
* Remove cipher update ([`21b9390`](https://github.com/Bluetooth-Devices/bthome-ble/commit/21b9390953341e540a42636f49b09ab17519ef5c))

## v2.2.1 (2022-11-07)
### Fix
* Multiple measurements fix ([`849deab`](https://github.com/Bluetooth-Devices/bthome-ble/commit/849deab688a83ba040e8f7e42598b4aa339d0460))

## v2.2.0 (2022-11-06)
### Feature
* Update dependencies ([`a3e9daf`](https://github.com/Bluetooth-Devices/bthome-ble/commit/a3e9dafcaa907ae3672c60df7e2da3ce8128b340))

### Fix
* Add tests for duration and temperature ([`552cbb8`](https://github.com/Bluetooth-Devices/bthome-ble/commit/552cbb8be03e62b1b9e2231ba4c658c658d375cd))
* Uv and duration sensors ([`4130c71`](https://github.com/Bluetooth-Devices/bthome-ble/commit/4130c71b01f4a1d733e11b153fbe50031b53b48b))

## v2.1.0 (2022-11-03)
### Feature
* New sensor types ([`1bbf778`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1bbf778887cb411d710a7787c3ae0f68a9a9eac2))

### Fix
* Update poetry file ([`90cf1ea`](https://github.com/Bluetooth-Devices/bthome-ble/commit/90cf1eaf4e8b474dfda13c6f579a46a3f08e95d2))

## v2.0.0 (2022-11-01)

### Breaking
* v2 release bump ([`93bfd22`](https://github.com/Bluetooth-Devices/bthome-ble/commit/93bfd22eff117f1cf2b98248b2ccf9b9dd90e6d8))

### Feature
* Remove object format and length byte ([`2f43a29`](https://github.com/Bluetooth-Devices/bthome-ble/commit/2f43a296cfb59fcb2938502801b3f4d12785358c))
* Remove predefined device info ([`cb16b35`](https://github.com/Bluetooth-Devices/bthome-ble/commit/cb16b35edec71c609ae12281f900f6f56d300e93))
* Multiple measurements of the same type ([`e57ed3d`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e57ed3d857164d373bba3ca86f368a9a4ed9030f))
* UUID V2 and adv_info byte ([`a4d6440`](https://github.com/Bluetooth-Devices/bthome-ble/commit/a4d64403dd359102762f2dbea777ccdf5e58a21d))

### Fix
* Parser not parsing multiple uuids ([#21](https://github.com/Bluetooth-Devices/bthome-ble/issues/21)) ([`e8d2646`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e8d2646bb73d39e7920a04243d862c9ed68ed2c0))
* Adjust button events ([`b796cdb`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b796cdb9d18703c12bfbc1a03602edae823df6f0))
* Logs and fix for wrong id ([`fc611c9`](https://github.com/Bluetooth-Devices/bthome-ble/commit/fc611c940295f7254bb89911d450e3abee544880))
* Fix v1 tests ([`8099cad`](https://github.com/Bluetooth-Devices/bthome-ble/commit/8099cadcf47efdfa10a4945b8cad6cbd9fad88f6))
* Add annotations ([`fb19043`](https://github.com/Bluetooth-Devices/bthome-ble/commit/fb19043808124ba9cfcea340c6144c9d19abc84a))
* Button and dimmer events ([`ac3b8fa`](https://github.com/Bluetooth-Devices/bthome-ble/commit/ac3b8faac93913cf93f2095053dee580407ae939))
* Wrong bthome device info byte ([`97d03ef`](https://github.com/Bluetooth-Devices/bthome-ble/commit/97d03efe657d875c06b6018453cc692a73a14531))
* Remove device_info_flag ([`f524294`](https://github.com/Bluetooth-Devices/bthome-ble/commit/f524294f29ad3df43066c5e13faf90c45e1e9b7d))
* Resolve comments ([`5a904f6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/5a904f6c97c2ad17ad706c224dbc5c2b2265f7b3))
* Improve coverage ([`f21a739`](https://github.com/Bluetooth-Devices/bthome-ble/commit/f21a739325ed2fe20d22256fe6e085c6404f8b12))
* Resolve comments review ([`e0d58a0`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e0d58a0e139f1b7928ff3407a56c02e40df9c5da))
* Remove mac parser and code cleaning ([`4a4fe68`](https://github.com/Bluetooth-Devices/bthome-ble/commit/4a4fe683b781caf05524f6a38290d8215bb3a4b6))

## v1.3.0 (2022-10-04)
### Feature
* Force new release adding events ([`8ae802a`](https://github.com/Bluetooth-Devices/bthome-ble/commit/8ae802a6a34eb9419504347a5a498bf9617063d1))

## v1.2.3 (2022-09-29)
### Fix
* Add missing comma ([`0f889e6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0f889e62b83247e7d0bb6f7edfeb695691a5f782))
* Remove unused imports ([`8f45606`](https://github.com/Bluetooth-Devices/bthome-ble/commit/8f45606d106f7cd43a1875c8d36226ab73745ede))
* Add test for encryption example ([`c323a31`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c323a31355592947f4c00cb0b6061f175f3a0686))
* Fix formatting issues ([`47017b6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/47017b6ed584a49a4ee2aa85ee678f3de2cd120b))
* Fix annotation ([`1bc8f72`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1bc8f72de8d807c333dc8ba767c5a0c2043dc4b1))
* Fix formatting issues ([`801679e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/801679eda2524f01d48e76cab6bf5310ade682ec))
* Remove use of predefined sensor wrapper ([`377adaa`](https://github.com/Bluetooth-Devices/bthome-ble/commit/377adaa576b03a76340570729dfd4ac2bf019b36))
* Remove unused lists ([`fd08fae`](https://github.com/Bluetooth-Devices/bthome-ble/commit/fd08faee434bc3b66aec241627407edc3eab4d80))

## v1.2.2 (2022-09-14)
### Fix
* Remove update binary sensor ([`e529f89`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e529f899eb7b9f38b65c36f5cc46d3df41e91f75))

## v1.2.1 (2022-09-13)
### Fix
* Remove empty line ([`5f7ba24`](https://github.com/Bluetooth-Devices/bthome-ble/commit/5f7ba2438f4a8e6bde341b74668514906364d070))
* Sort import order ([`ba5afd1`](https://github.com/Bluetooth-Devices/bthome-ble/commit/ba5afd11bea7678f0a9af50ad9c4a08a0800b62c))
* Always use bthome device classes ([`15fa937`](https://github.com/Bluetooth-Devices/bthome-ble/commit/15fa93718d7b506cc25e80831f7612423bd13306))

## v1.2.0 (2022-09-09)
### Feature
* Add binary sensors ([`c83d0da`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c83d0dab1aa44730976c0185c73d928a72a01b75))

### Fix
* Flake8 error ([`4ed3312`](https://github.com/Bluetooth-Devices/bthome-ble/commit/4ed3312453c35d1911bb463a2c0b35310626e84f))
* Update poetry lock file ([`477f974`](https://github.com/Bluetooth-Devices/bthome-ble/commit/477f974aba5ef9d469975473902994d01ed00181))
* Remove unused import ([`44f171a`](https://github.com/Bluetooth-Devices/bthome-ble/commit/44f171aad9375877dfba4f55d6f6f2ede12ccdad))
* Mypy error ([`716f626`](https://github.com/Bluetooth-Devices/bthome-ble/commit/716f626729080c451c24dd7da242d97709d620a7))

## v1.1.1 (2022-09-08)
### Fix
* Add binary sensor device class ([`d48783e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d48783e1a7c3a3a719fc7dca9f08feb034660507))

## v1.1.0 (2022-09-06)
### Feature
* Binary sensor support ([`35ec5e1`](https://github.com/Bluetooth-Devices/bthome-ble/commit/35ec5e1d328038b328c4b793e9fe70c354d731dd))

### Fix
* Fix tests ([`ffce92d`](https://github.com/Bluetooth-Devices/bthome-ble/commit/ffce92d599d1831ae241e10bddb874b5d5761a15))
* Fix flake8 tests ([`b428339`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b428339e38f28caf17adc02b48a9585f05b629d1))

## v1.0.0 (2022-09-01)
### Feature
* Change name of bthome with capital h ([`cf3c702`](https://github.com/Bluetooth-Devices/bthome-ble/commit/cf3c702ca4b2e25cc15a74379deeb84a949427d7))
* Bthome with capital h ([`c307462`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c3074628da771ce78810538e8776797aae4df147))

### Breaking
* bthome with capital h ([`c307462`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c3074628da771ce78810538e8776797aae4df147))

## v0.5.2 (2022-08-30)
### Fix
* Use full name for bparasite ([`bcd07da`](https://github.com/Bluetooth-Devices/bthome-ble/commit/bcd07da262009383f4e67592fec6614937fe847f))

## v0.5.1 (2022-08-29)
### Fix
* Fix tests for non standard device classes ([`d48ec31`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d48ec31005c35d8f064bf2717c648b058bb1b468))
* Use update_sonsor for other device classes ([`eabde87`](https://github.com/Bluetooth-Devices/bthome-ble/commit/eabde8776ac6cdf9e7d1753aa4b2909d769de37d))

## v0.5.0 (2022-08-28)
### Feature
* Add new sensor types ([`15ac53a`](https://github.com/Bluetooth-Devices/bthome-ble/commit/15ac53af864ba3446973a4518f6dd30509bc1347))

### Fix
* Add test for b-parasite ([`ecbb823`](https://github.com/Bluetooth-Devices/bthome-ble/commit/ecbb823ce604903a391df8c1e3a4f4d1558abc74))
* Bump sensor-state-data ([`e3e21af`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e3e21af1a7df36891aa504891afdab9caef82b06))
* Lint errors ([`8c3697e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/8c3697e479f20ce41763fbd32c9872af6974d990))

## v0.4.0 (2022-08-26)
### Feature
* Get manufacturer from name ([`1e66c90`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1e66c90cbe884852dab74c57708ba702ecafc736))

## v0.3.8 (2022-08-25)
### Fix
* Failing reauth ([`7b3b0d2`](https://github.com/Bluetooth-Devices/bthome-ble/commit/7b3b0d2c66546c1b2d55d42ec95d94a0d7117ab5))

## v0.3.7 (2022-08-25)
### Fix
* Code format ([`f5c531f`](https://github.com/Bluetooth-Devices/bthome-ble/commit/f5c531f73ea4be7dd749f0301bb1e486a0493106))
* Use short address from data tools ([`722a97f`](https://github.com/Bluetooth-Devices/bthome-ble/commit/722a97f513b7c6db63173433dea629ba59445fda))

## v0.3.6 (2022-08-24)
### Fix
* Flake8 error ([`cc9f077`](https://github.com/Bluetooth-Devices/bthome-ble/commit/cc9f077ab9ce3685305a2407b17150a6e7f9bac5))
* Table format ([`eca5d42`](https://github.com/Bluetooth-Devices/bthome-ble/commit/eca5d42e710c5edadc190f289d88219f43699ee6))
* Units of voc ([`0f4c773`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0f4c773c02310a3546c2687cf5d18d31677c0549))

## v0.3.5 (2022-08-24)
### Fix
* Workaround for empty service_uuids ([`2cab081`](https://github.com/Bluetooth-Devices/bthome-ble/commit/2cab081c591de7807c02424819bfca243d360b69))

## v0.3.4 (2022-08-23)
### Fix
* Length check ([`9817c84`](https://github.com/Bluetooth-Devices/bthome-ble/commit/9817c84f78993c743c354a09789354c6fa600a18))

## v0.3.3 (2022-08-23)
### Fix
* Minor change to force a new release ([`a55133a`](https://github.com/Bluetooth-Devices/bthome-ble/commit/a55133a243c3b40b4a1a330a70f4aa8930d5dc8a))

## v0.3.2 (2022-08-21)
### Fix
* Supported sensor fix ([`0bc45bf`](https://github.com/Bluetooth-Devices/bthome-ble/commit/0bc45bf822da65d705823daff57881c917b9c8fc))

## v0.3.1 (2022-08-21)
### Fix
* Remove double mac from name ([`eb77ad8`](https://github.com/Bluetooth-Devices/bthome-ble/commit/eb77ad8d947d53bfc585515cc512d088913f69e1))

## v0.3.0 (2022-08-19)
### Feature
* Add encryption support ([`e299228`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e299228e02313c154027bdef017a64db5d7fbe4c))

### Fix
* Isort ([`d85e345`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d85e345ddfc4380c317df83774ef9fe61594d037))

## v0.2.2 (2022-08-18)
### Fix
* Auto release test ([`8fa2ba6`](https://github.com/Bluetooth-Devices/bthome-ble/commit/8fa2ba6831e793652d0658292730942345585bf5))

## v0.2.1 (2022-08-18)
### Fix
* Auto release ([`1eac241`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1eac2415693e1a60d948e023fce5b8db108d56c1))

## v0.2.0 (2022-08-18)
### Feature
* **sensor-state-data:** Update dependency ([`b624ef5`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b624ef51b40f371eb23dfe2a66b2ecc1752832fd))
* **poetry:** Update dependencies ([`b0177f4`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b0177f4427464e54262e1ca087d94bad570087a7))

### Fix
* Delete poetry log ([`1376c47`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1376c473aa5f9c3783f9f2b03dfccf483f224335))
* Update sensor-state-data version ([`132cf9e`](https://github.com/Bluetooth-Devices/bthome-ble/commit/132cf9e74560a2abd5e263ddda04c70c9a6a1cfd))

## v0.1.0 (2022-08-18)
### Feature
* Initial release ([`c097555`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c0975559955bddab4c96aa993e381107b4f7c152))

### Fix
* Increase line length ([`1dd1baa`](https://github.com/Bluetooth-Devices/bthome-ble/commit/1dd1baa45549b2739ca0e7d787046cf2dfc637d4))
* Increase line length ([`c8d9a56`](https://github.com/Bluetooth-Devices/bthome-ble/commit/c8d9a56a9d61390b9617b7ec0a8ea83d267615d6))
* Flake 8 errors ([`71fae3c`](https://github.com/Bluetooth-Devices/bthome-ble/commit/71fae3c1c008874e8c5af492b714c035c7e1a872))
* Flake8 errors ([`dd7a283`](https://github.com/Bluetooth-Devices/bthome-ble/commit/dd7a283582b48556a9212f3702d287111a3847b3))
* Flake8 errors ([`b36bb2d`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b36bb2d4c79ba1823d290449a65965ee01145dee))
* Mypy error ([`1364971`](https://github.com/Bluetooth-Devices/bthome-ble/commit/13649712943bfacacf6e3e2e53a2ea677073962e))
* Formatting conflicts ([`e2548b0`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e2548b00485e3485ee91715b5229a60b4104aa01))
* Formatting errors ([`7bef4a3`](https://github.com/Bluetooth-Devices/bthome-ble/commit/7bef4a34beb38d94bc023aefc964a8945e43ff6b))
* Flake8 errors ([`8634293`](https://github.com/Bluetooth-Devices/bthome-ble/commit/863429339ad6e1f1b8a75b0bc06283979110783a))
* Bump sensor-state-data ([`d9e409d`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d9e409dbb5612fba786338f35a4354d1e1a0463c))
* Linting errors ([`b1dc181`](https://github.com/Bluetooth-Devices/bthome-ble/commit/b1dc1815cf49100b94f99430948757f0790a5a04))
* Linting errors ([`d47bfc9`](https://github.com/Bluetooth-Devices/bthome-ble/commit/d47bfc99223a7bb5237db7ced36b3e73992b599e))
* Linting errors ([`e33c68f`](https://github.com/Bluetooth-Devices/bthome-ble/commit/e33c68f7698a3ff5ee1ac9bc3bcb408d9458aae5))
