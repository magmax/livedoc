# LiveDoc

[LiveDoc] is the easiest way to maintain documentation up to date with code, because it allows to use the documentation as tests.


## Basic usage

It allows to assign a value to a variable. For example, the simple command `[5](- 'a = TEXT')` has created the variable ``a`` with the value [5](- 'a = TEXT').

Now you can check that variable ``a`` has the value of [5](- 'a == TEXT') with just `[5](- 'a == TEXT')` expression. When the comparition fails, the output is verbose. For example, you can ensure `[4](- 'TEXT == a')`, resulting in [4](- 'TEXT == a').

Additionally, you can print the ``a`` value just assigning its value to ``OUT`` variable, like `[ ](- 'OUT = a')`, which will show [ ](- 'OUT = a')


## Tables

In order to create examples about usage, you can use tables. This is an easy way to show the difference between several inputs:

| Factor 1 | Factor 2 | Result |
| --- | --- | --- |
| [2](- 'f1=TEXT')  | [2](- 'f2=TEXT') | [4](-  'TEXT == f1*f2') |
| [3](- 'f1=TEXT')  | [3](- 'f2=TEXT') | [9](-  'TEXT == f1*f2') |
| [4](- 'f1=TEXT')  | [4](- 'f2=TEXT') | [16](- 'TEXT == f1*f2') |
| [5](- 'f1=TEXT')  | [5](- 'f2=TEXT') | [25](- 'TEXT == f1*f2') |

This can be done in the obvious way:

    | Factor 1 | Factor 2 | Result |
    | --- | --- | --- |
    | [2](- 'f1=TEXT')  | [2](- 'f2=TEXT') | [4](-  'TEXT == f1*f2') |
    | [3](- 'f1=TEXT')  | [3](- 'f2=TEXT') | [9](-  'TEXT == f1*f2') |
    | [4](- 'f1=TEXT')  | [4](- 'f2=TEXT') | [16](- 'TEXT == f1*f2') |
    | [5](- 'f1=TEXT')  | [5](- 'f2=TEXT') | [25](- 'TEXT == f1*f2') |

But you can use shortcuts too to get the same:

| [Factor 1](- 'f1=TEXT') | [Factor 2](- 'f2=TEXT') | [Result](- 'TEXT == f1*f2') |
| --- | --- | --- |
| 2   | 2   | 4   |
| 3   | 3   | 9   |
| 4   | 4   | 16  |
| 5   | 5   | 25  |

just setting the titles instead of each cell:

    | [Factor 1](- 'f1=TEXT') | [Factor 2](- 'f2=TEXT') | [Result](- 'TEXT == f1*f2') |
    | --- | --- | --- |
    | 2   | 2   | 4   |
    | 3   | 3   | 9   |
    | 4   | 4   | 16  |
    | 5   | 5   | 25  |





## Fixtures

You can add any code you want in order to be used in your documentation. It is as simple as adding a `.py` file with the same name than the documentation file. For example, this file is called `index.md`, so [LiveDoc] has loaded the file `index.py` in the same directory. This fixture contains a method that duplicates any number, and can be called whenever you want. For example, you can check that `[10](- 'TEXT == duplicate(5)')`: [10](- 'TEXT == duplicate(5)')



[LiveDoc]: https://pypi.python.org/pypi/livedoc



## Exceptions

If an exceptions is raised, it is easy to discover it, like if you divide [1](- 'n=TEXT') between [0](- 'd=TEXT'), resulting in ['whatever'](- 'n/d').

It can happen inside a table too:

| [Numerator](- "n = TEXT") | [Denominator](- "d = TEXT") | [Division](- "TEXT == n/d") |
| --- | --- | --- |
| 2 | 1 | 2 |
| 2 | 0 |  |
| 2 | -1 | -2 |
