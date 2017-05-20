# UTF-1

An encoding where the shortest way to encode a character is 1 bit!

Note: I found out about the deprecated actual [UTF-1](https://en.wikipedia.org/wiki/UTF-1) after I wrote this. I need a better name for this.

## Encoding

To encode a sequence of Unicode code points is simple.

For every character:

* Write `1` times the code point bits.
* Write a `0` bit.

Then pad with `1` to the nearest multiple of 8.

It's really that simple!

Example:

```python
'Hello, world!' ->
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xfb\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xbf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xfb'
````

## Decoding

Encoding is just as simple!

Read the number of consecutive `1` bits before reaching a `0`. Write the character with the code point of the number of consecutive `0`s. Discard the `0`.  
Repeat.  
If you reach the end without encountering a `0`, it is padding, so discard it.

Example:
```
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xfb\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xbf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xfb' ->
'Hello, world!'
```

Every arbitrary sequence of bytes is valid UTF-1. Except Unicode limits code points to be below 1114111. Just use a better character set if this happens.

## Advantages of UTF-1

Say you have a sequence of `'\x00'` and `'\x01'`s. Let's say for a moment that you forgot that you can read them as bits, and then store them as 1 bit each. If you were to encode them with an encoding like UTF-8, it would take _a whole byte_ for every character. With UTF-1, it takes 1 bit for `'\x00'`, and 2 bits for `'\x01'`.

```
'\x00\x01\x00\x00\x01\x00\x00\x00\x00\x01\x01\x00\x00\x01\x00\x01\x00\x01\x01\x00\x01\x01\x00\x00\x00\x01\x01\x00\x01\x01\x00\x00\x00\x01\x01\x00\x01\x01\x01\x01\x00\x00\x01\x00\x01\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x01\x01\x00\x01\x01\x01\x00\x01\x01\x00\x01\x01\x01\x01\x00\x01\x01\x01\x00\x00\x01\x00\x00\x01\x01\x00\x01\x01\x00\x00\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01'

UTF-8:
0000000000000001000000000000000000000001000000000000000000000000000000000000000100000001000000000000000000000001000000000000000100000000000000010000000100000000000000010000000100000000000000000000000000000001000000010000000000000001000000010000000000000000000000000000000100000001000000000000000100000001000000010000000100000000000000000000000100000000000000010000000100000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000100000001000000010000000000000001000000010000000100000000000000010000000100000000000000010000000100000001000000010000000000000001000000010000000100000000000000000000000100000000000000000000000100000001000000000000000100000001000000000000000000000000000000010000000100000000000000000000000100000000000000000000000000000000000000010000000000000000000000000000000000000001
(832 bits, or 104 bytes!)
UTF-1:
0100010000010100010010010100101000010100101000010100101010100010010100000100000001010100101010010100101010100101010001000101001010000101000100000100000101111111
(160 bits, or 20 bytes!)
```

UTF-8 did **520%** worse! So why wait? Switch over your file systems now!

#### Disadvantages

<sup><sup>What? I already told you to change your encoding! You can't read this US-ASCII.</sup></sup>
