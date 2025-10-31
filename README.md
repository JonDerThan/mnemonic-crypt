# MnemonicCrypt

Encrypts data (or another mnemonic) and generates mnemonics for the used salt
("encryption entropy") and ciphertext.

Assume you created a Bitcoin wallet, which is uniquely identified by some
mnemonic (a sequence of 12 or more words, e.g. "able zoo ..."). Most wallets
recommend writing the mnemonic down somewhere, but that leaves your wallet open
to anyone gaining access to this piece of paper. You may want to encrypt the
mnemonic but any normal encryption scheme forces you to store the ciphertext
(the encrypted mnemonic) digitally, which makes you vulnerable to malware and
introduces a risk of data loss.

MnemonicCrypt encrypts your mnemonic (or any other arbitrary binary data) and
then formats the result itself as a mnemonic, which can be written down safely.
Encrypting 12 words results in 36 words of encrypted data, a 24 word mnemonic
fits into 48 words when encrypted.

## Getting Started

There are several methods for running this application, you can freely choose
any one of the options below. The easiest method (the one you should use if you
don't want to install Python) is using the standalone executable. The
recommended method is using PyPI.

### Standalone Executable

1. Go to the [Releases](https://github.com/JonDerThan/mnemonic-crypt/releases/latest)
page.
2. From the release assets (scroll down), download the correct file for your
system, e.g. `mnemonic_crypt_windows_v1.2.3.zip`. Extract the zip file.
3. Go to the extraction path and doubleclick `mnemonic_crypt_gui.exe`.

Note: it is possible that the executable doesn't work. In this case please try
one of the other methods and file a new [Issue](https://github.com/JonDerThan/mnemonic-crypt/issues/?q=is%3Aissue%20state%3Aopen%20standalone)
if one doesn't already exists (please put "Standalone Executable" somewhere in
the title).

### Install with PyPI

1. Run `python3 -m pip install mnemonic-crypt`.
2. Run `mnemonic_crypt_gui` to open the GUI, for the CLI run
`mnemonic_crypt [args]`.

### Run with pipx

1. Follow the [pipx](https://pipx.pypa.io/latest/installation/) installation
guide.
2. Run `pipx run --spec mnemonic-crypt mnemonic_crypt_gui` (uses PyPI) or
`pipx run --spec git+https://github.com/JonDerThan/mnemonic-crypt.git@main mnemonic_crypt_gui`
(uses the git repository).

## Usage

### Graphical User Interface (GUI)

1. Copy and paste your mnemonic into the `Plain mnemonic` field. If you want to
encrypt some other data, format it as hex and paste it into the `Plain data`
field instead.
2. Type in some password and press the `Generate` button.
3. The `Salt (mnemonic)` as well as the `Encrypted mnemonic` should be filled
out automatically. Now write down **ALL** of the following fields:
- `Salt mnemonic`
- `Encrypted mnemonic`
- `KDF parameters`

The result should look like this:

```
Salt mnemonic
1. layer     2. slogan   3. weird  4. gas
5. original  6. buffalo  7. ...

Encrypted mnemonic
1. anchor    2. guide    3. enemy  4. sauce
5. measure   6. neglect  7. ...

KDF: $argon2id$v=19$m=65536,t=3,p=4
```

To decrypt your data, simply fill in these values and click `Generate` again.

### Command Line Interface (CLI)

The application can be run in multiple ways, one such way is described in
[Run with pix](#run-with-pipx). For brevity, the commands here are written with
`mnemonic_crypt [args]` instead of `pipx run --spec . mnemonic_crypt [args]`
although you may have to use the latter one.

The view full documentation of the CLI, run `mnemonic_crypt --help`. A few
examples are listed below.

#### Encrypting Data

```sh
mnemonic_crypt encrypt 'lion blush obey agree remove improve aspect dawn giraffe maze belt wolf'
```

The program prompts you for a password...

**Output:**

```
Encrypted mnemonic:
 1. mechanic     2. miss         3. coach        4. maid    
 5. trouble      6. since        7. stairs       8. obey    
 9. grass       10. wheat       11. suspect     12. script  
13. admit       14. category    15. portion     16. assume  
17. garage      18. grain       19. matter      20. banner  
21. donor       22. drive       23. wash        24. over    

Salt:
 1. truly       2. hub         3. slim        4. winner 
 5. roast       6. meadow      7. banana      8. stereo 
 9. never      10. bag        11. cattle     12. confirm

KDF:
$argon2id$v=19$m=65536,t=3,p=4
```

Note down all of the information! Losing only one of the 3
(encrypted data/salt/KDF) will result in an irrevocable loss of your data!

#### Decrypting Data

```sh
mnemonic_crypt decrypt \
    --kdf-params '$argon2id$v=19$m=65536,t=3,p=4' \
    --salt 'truly hub slim winner roast meadow banana stereo never bag cattle confirm' \
    'mechanic miss coach maid trouble since stairs obey grass wheat suspect script admit category portion assume garage grain matter banner donor drive wash over'
```

The program prompts you for a password...

**Output:**

```
Decrypted mnemonic:
 1. lion        2. blush       3. obey        4. agree  
 5. remove      6. improve     7. aspect      8. dawn   
 9. giraffe    10. maze       11. belt       12. wolf
```

#### Programmatic Usage

You may not want the output of the program to be formatted in tables, for
example when using this application programmatically. In this case you can
set the `--no-pretty-print`/`-u` flag, which outputs the data like this: for
encryption, the encrypted mnemonic/salt/kdf are each printed into one line; for
decryption only the decrypted mnemonic is printed as a single line. Note that
the "Calculated key in ..." message is printed to `stderr` so you should be able
to parse the programs output by just reading `stdin`.

For programmatic usage you probably also want to supply the password as a
command line argument with `--password`/`-p`.

## Non-Technical Scheme Description

### Key Derivation Function

Encryption isn't as straightforward as one might think. The standard symmetric
encryption algorithm is AES; to encrypt data with it, we need some key at the
very least. The key length in AES can be between 128-256 bits. If you were to
randomly generate this key and kept it a secret, no one would be able to decrypt
your data.

You are probably not able to memorize 128 random bits though, instead of
actually using random bits, you prefer to use some password. Technically you
could use the binary representation of your password as the AES key; this would
however be incredibly insecure.

To decrypt your data without knowing the key, an attacker would have to iterate
every possible key and try to decrypt your data with it by using the AES
algorithm. Because the algorithm runs very fast, a huge number of possible keys
can be checked in a very short amount of time.

Now, with 128 random bits, an attacker would have to check 2^128 keys, which
still poses an infeasible problem, despite the speed of AES. Your password
however, could easily be found in a very short time, no matter how secure you
think it is.

Assume now, instead of using a password as the key directly, we first transform
the password with a `Key Derivation Function` (KDF). The KDF produces a
pseudo-random output, any password you put into it produces 256 bits that appear
random in every practical sense. These bits are used as a key for the actual
encryption.

Any attacker that were to try to guess the AES key directly now would have to
check every possible combination of these 256 bits, which would be just as hard
as if we had generated these bits randomly.

The only feasible attack would consists of again trying to guess
our password. For this the attacker has to first put every attempted password
through the exact same KDF that we used.

If this KDF was a very fast algorithm this would introduce no additional
security; we can however choose some very slow algorithm, which drastically
reduces the number of guesses an attacker could perform in a set time.

Here, the KDF used is [Argon2](https://en.wikipedia.org/wiki/Argon2),
specifically the `Argon2id` version. This algorithm is recommended by e.g.
[OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

Argon2 has some parameters that specify how exactly the algorithm runs.
Increasing these parameters increases the computational effort needed to derive
the key from the input password. Try to modify the parameters a bit and see how
long the program freezes when pressing `Generate`.

Note that these parameters are necessary to decrypt your data again; you should
note them down along with your encrypted data, otherwise you may lose access to
it. The default values may change in the future, so don't depend on them being
filled in automatically.

### Salt and IV

Although the KDF can significantly slow down an attacker, nothing prevents them
from attempting to guess your password before they even gain access to your
encrypted data.

A KDF will always produce the same output when given the same input. Adversaries
can easily build a database of a large amount of possible inputs and their
corresponding outputs. Trying to "guess" your password would then just consist
of looking it up in this list.

To avoid this, we ideally also want to randomize the input to the KDF a bit.
This is done by just appending some randomly generated value, called the *salt*
before transforming it with the KDF. If your password is `password1`, the input
to the KDF may be `password1jioqwenafiqowe`. It is highly unlikely that there
exists a database where for this exact text a KDF output was already calculated.

For this and some other reasons, any encryption scheme must generate some random
value. To decrypt your data again, this salt must be of course known; that is
why you must note down the `Salt mnemonic` as well, which is essentially just a
random value.

Coincidentally, the actual encryption algorithm used here (AES-CBC) also needs
a random value, the so called *initialization vector* (IV). The salt used for
the KDF is also used as this IV.

## Background and Technical Info

The mnemonics used here are specified by the *Bitcoin Improvement Proposal*
(BIP) 39
([link](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)). The
scheme consists of a list of 2^11 = 2048 distinct words, where every word
encodes 11 bits, based on their respective position in the list. A Bitcoin
wallet can be uniquely identified by some entropy (commonly 128 random bits).
The mnemonic encoding scheme appends a 4 bit checksum and then translates blocks
of 11 bits into a total of `(128 + 4) / 11 = 12` words.

This project decodes the entropy from this mnemonic (the checksum is also
removed) and then encrypts this as binary data.

### Detailed Scheme Description

#### BIP 39 Encoding

The official encoding can't be used to represent any arbitrary data, because a
word represents 11 bits (instead of a multiple of 8). To remedy this, the
encoding here zerofills the rightmost bits, s.t. (together with the checksum)
a multiple of 11 is reached. A padding for e.g. 9 is expressed in the mnemonic
like this `... able zoo p9`. The checksum is calculated before the padding is
applied, the amount of checksum bits is determined before as well.

Mnemonics generated by Bitcoin wallets will not include such a padding.

#### Encryption Process

**Input:**  Binary data (possibly decoded from a mnemonic). A password.
**Output:** A random salt (128 bits). A BIP-39 encoded encrypted representation
of the data.

1. A random salt is generated.
2. The user-specified password (utf-8 encoded) and the random salt
(in binary form) is transformed by the KDF `Argon2id` to form a 256 bit
pseudo-random value. The Argon2id parameters can be configured by the user.
3. The input data is padded with `PKCS7` so that its size in bits is a multiple
of 128 (the AES block length).
4. The padded data is encrypted with `AES-CBC`. The raw bits of the previously
generated salt is used as the IV. The KDF output is used as the key.
5. The encrypted data is encoded with the `BIP-39` scheme.

Note: the salt is presented as a mnemonic to the user but the calculations only
use its normal binary form.

#### Decryption process

**Input:** Encrypted data in BIP-39 representation. A salt. A password.
**Output:** Binary data (additionally represented as a mnemonic).

1. Decode the mnemonic so that the encrypted data is in binary form.
2. Use the specified password and salt to generate the 256 bit AES key with
`Argon2id`.
3. Decrypt the binary data with `AES-CBC`, use the KDF output as the key and the
salt as the IV.
4. Unpad the decryption output with `PKCS7`.
5. Encode the end result with `BIP-39`.

## FAQ

### Why not just use the BIP-39 passphrase

The Bitcoin Improvement Proposal that defines the mnemonic encoding actually
also allows for a passphrase that is used in conjunction with the mnemonic to
calculate the actual seed for the Bitcoin wallet. There are two issues I see
with that passphrase:

1. The KDF used for the passphrase in BIP-39 seems to me to be relatively
unsecure by todays standard. In the future the passphrase may become trivially
easy to brute-force.
2. Not every Bitcoin wallet supports this passphrase. If you choose to use a
passphrase you may simply be locked out from using a certain wallet, as long
as they continue to not support the passphrase.

By using this program, you use a KDF that is very secure as of now. Because this
is completely decoupled from the Bitcoin technology, at any time in the future
you can catch up to the then-modern security, by encrypting your mnemonic with
future technology and disposing of your old encrypted mnemonic.

Because you have full control over the KDF you are also able to make very simple
passwords relatively secure by just setting the KDF parameters to very big
values (although I would not recommend this if you aren't very sure what you are
doing).

Additionally, you can also use this program to encrypt any other data, which is
not possible with the BIP-39 passphrase.

### Can I store the salt and encrypted mnemonic at different locations

I think (see [Addendum](#addendum) below) that the encrypted mnemonic is
practically impossible to crack without having access to the salt, even when
knowing the password. The seed itself does not include any information about
the original data. I therefore think that this is a good way to distribute the
secret over multiple places.

Note however that you will loose access to your data should one of the two get
lost. I also do not think that such measures are likely necessary. I would
presume losing your data is the biggest risk concerning the mnemonic.

### How will I decrypt my data if this program stops working

Any software engineer should be able to decrypt your data given the encryption
scheme description in this file. For this reason you may want to print the
[Technical Info](#background-and-technical-info) and physically store it
alongside your encrypted mnemonic.

This program is however written in a very popular programming language, and is
using libraries that are very unlikely to stop working in the foreseeable
future. I would advise you to download and backup this program somewhere though,
should this repository go offline sometime.

## Addendum

**Note:** I am not a security professional. I can not guarantee without
uncertainty that the encryption is as secure as it should be.
