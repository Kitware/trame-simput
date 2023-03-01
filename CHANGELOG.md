# Changelog

<!--next-version-placeholder-->

## v2.3.1 (2023-03-01)
### Fix
* **widgets:** Add Simput.register_layout() ([#15](https://github.com/Kitware/trame-simput/issues/15)) ([`0c84866`](https://github.com/Kitware/trame-simput/commit/0c848668a6a96ab9d6c54078c77eb297b8a0dd05))

## v2.3.0 (2023-02-28)
### Feature
* **widgets:** Toggle disable/readonly for inputs ([`11552a9`](https://github.com/Kitware/trame-simput/commit/11552a90fc9bf9b56d7a00a47483652d746f4714))

## v2.2.6 (2023-02-23)
### Fix
* **version:** Add __version__ ([`f6b755c`](https://github.com/Kitware/trame-simput/commit/f6b755cb48a1efbea15f285ca13e73bc4a365985))

## v2.2.5 (2023-01-12)
### Fix
* **data:** Race condition between update and dirty ([`7c92db1`](https://github.com/Kitware/trame-simput/commit/7c92db150affa1a623a7a6ce0399aca644baea79))
* **notification:** Only trigger change on domain/ui when changed ([`6d5ca00`](https://github.com/Kitware/trame-simput/commit/6d5ca00f4e6e312da34f0bd56aed5814a40992b5))

## v2.2.4 (2022-12-20)
### Fix
* **domain:** Test against js string undefined and null ([`8fc0490`](https://github.com/Kitware/trame-simput/commit/8fc049066e5c7484fde5c68011e59f7f24478fa2))

## v2.2.3 (2022-11-10)
### Fix
* **domains:** No exception with invalid id ([`c6a069f`](https://github.com/Kitware/trame-simput/commit/c6a069fe35b8a005c25bd5a1b0a2aeecccb8daad))

## v2.2.2 (2022-11-02)
### Fix
* **domain:** Remove int constraint on proxy id ([`c8cf5bd`](https://github.com/Kitware/trame-simput/commit/c8cf5bdaee3e31d60e33f2adfbfe21d7ade6e69e))

## v2.2.1 (2022-10-25)
### Fix
* **proxy:** Log warning if no definition was found in set_property ([`6d432eb`](https://github.com/Kitware/trame-simput/commit/6d432ebec4860c1165c524f650d1cc507e7b62b2))

## v2.2.0 (2022-10-25)
### Feature
* **proxy:** Enable instantiation with existing object ([`7ae48bc`](https://github.com/Kitware/trame-simput/commit/7ae48bc6bc6372042af72d5873114df817fe50a8))

### Fix
* **widgets:** Make array parameters use multiple rows ([`0454339`](https://github.com/Kitware/trame-simput/commit/045433948748d4f5f9d842ae1c4482127520a727))

## v2.1.1 (2022-10-21)
### Fix
* **proxy:** Handling of false-like initial value ([`b5434fe`](https://github.com/Kitware/trame-simput/commit/b5434fe2fea578e93e9f4fa61c3d69f40a3e8342))

## v2.1.0 (2022-09-09)
### Feature
* **proxy:** Enable overriding proxy id ([`e94344a`](https://github.com/Kitware/trame-simput/commit/e94344a8495835b00e011dbc78843ee70857e2a0))

### Documentation
* **readme:** List examples ([`ca78816`](https://github.com/Kitware/trame-simput/commit/ca78816abc98040f305c5af2a199533c02c6d468))
* **readme:** List examples ([`505c73f`](https://github.com/Kitware/trame-simput/commit/505c73f8ea93c88e98469e179c7d9c472b68705f))
* **readme:** List examples ([`12b6ce5`](https://github.com/Kitware/trame-simput/commit/12b6ce5e595c784f1ac97fe062dd5247173278db))
* **general:** Update project usage and doc ([`bba905d`](https://github.com/Kitware/trame-simput/commit/bba905d05e2588456685a715a0ba6c3591941680))

## v2.0.7 (2022-08-22)
### Fix
* **domain:** Handle invalid domain request ([`dc2cc9c`](https://github.com/Kitware/trame-simput/commit/dc2cc9c98e485317e5de4a5f3b5d9bdfe1dc329c))

### Documentation
* **examples:** Fix attribute name to match latest api ([`987aad8`](https://github.com/Kitware/trame-simput/commit/987aad86414a83ad19ad01fd82ae91fa153ed75a))

## v2.0.6 (2022-08-22)
### Fix
* **widgets:** Self._helper.changeset is a property ([`8e7f540`](https://github.com/Kitware/trame-simput/commit/8e7f540c2267c6c686fb9811436da28d5744b12a))

## v2.0.5 (2022-08-18)
### Fix
* **domain:** Don't lookup domain with invalid id ([`f9a0f55`](https://github.com/Kitware/trame-simput/commit/f9a0f55dffa2c84a0dc4a7768e41e0ac0a8ae9c5))

## v2.0.4 (2022-08-18)
### Fix
* **domains:** Make sure to clear all domains when reloading ([`4ed2be6`](https://github.com/Kitware/trame-simput/commit/4ed2be658d5a0b9bd74adf1d5bf79864791904b9))

## v2.0.3 (2022-08-17)
### Fix
* **item_id:** The JS will always convert it to a string ([`43be2f0`](https://github.com/Kitware/trame-simput/commit/43be2f09e75a9903344fa775f2e73cd0f967b79b))

## v2.0.2 (2022-08-17)
### Fix
* **reload:** Expose reload helper on Simput widget ([`1d5de80`](https://github.com/Kitware/trame-simput/commit/1d5de80a8d406362e00422fa41dee8b589cce4b2))

## v2.0.1 (2022-06-02)
### Fix
* **registration:** Allow custom name registration ([`06c689e`](https://github.com/Kitware/trame-simput/commit/06c689ebb7c45dccba68a2b6f8adde6be74c02c3))
* **vtk:** VTK example is now working ([`0706987`](https://github.com/Kitware/trame-simput/commit/0706987a117efa494055d92b34d06672e1943a96))

### Documentation
* **examples:** Add some examples ([`8256135`](https://github.com/Kitware/trame-simput/commit/825613568a1fa729d0785607dc3268b61b46f423))
