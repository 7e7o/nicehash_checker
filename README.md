NiceHash chekcer
================

Nicehashの未払い残高・収益性・walletの残高を表示するスクリプト。ステータスバー系のプログラムから呼ばれることを想定

## Requirment

* Python 3.5+
* requests

## Usage

```
./nhchecker.py [-h] [-m] [-r] {stats,balance}

positional arguments:
  {stats,balance}

optional arguments:
  -h, --help            show this help message and exit
  -m, --milli           単位をmBTCにする
  -r, --human_readable  単位を付けて表示
```

最初に引数なしでnhchecker.pyを実行するとnhchecker.pyと同じディレクトリにuser.jsonの雛形が作られるので、エディタで開いてaddrにBTCアドレス、IDにAPI ID、keyにAPI Key(ReadOnlyでOK)を埋めてください。API IDとAPI KeyはNiceHashにログインし、Settings -> APIにあります。

## Example

```
% ./nhchecker.py -m -r stats
0.502 mBTC
0.485 mBTC/dat

% ./nhchecker.py balance
0.00777
```

## License
MIT