{{../markdown_header.txt}}

# Tips for Writing a Paper #

For some exceptionally well written papers, take a look at the work of Richard Rogerson.

## Structure of the presentation

Separate the presentation of what you do from the discussion of why you do it. Brief comments mixed in with the model presentation are ok. Long discussions make it hard to follow what you actually do.

Separate the presentation of the model from the derivation of its implications. It is very confusing to read a paper that mixes assumptions with results. First present the model. Define equilibrium. Then derive properties of the equilibrium.

There is a standard structure for presenting a **model**:

1. Demographics
2. Endowments
3. Preferences
4. Technologies
5. Market arrangements

Only once these have been stated is it acceptable to talk about equilibrium properties or agents' problems. Next, describe the agents' problems, and define an equilibrium.

Your **introduction** should answer the following questions (due to Lee Ohanian):

* What is the question to be answered?
* Why is it important? (Often obvious)
* How is it approached?
* Why is the approach reasonable?
* What is the main result?
* How does the paper change the way I think about economics? What is the contribution?
* What is new relative to the literature?


## The process of writing

**Nice wording comes last**

* First decide on what you want to write. Just write that down. Focus on structure. Ignore wording and formatting.
* Only when everything is in place does it make sense to worry about construcing nice sentences.
* When you write a section, ask yourself: what is the message of this section? And then write the answer to that question as the section's intro sentence.

Do not mix levels of abstraction (a rule borrowed from programming). When you discuss high level arguments (e.g. in the Introduction), do not mix in details.

Think of your document as a nested list or an outline. There should be a place (the Intro) where the reader can get the entire story (minus detail) on about one page. Then think of each section as elaborating the details of the overall argument. Ideally, the reader should be able to read the level 2 sections (skipping the level 3s) and get the entire argument again, just with a bit more detail.

The level 3 sections then provide even more detail. Each such section should by itself make a self-contained point.

PS: I wish there was a technology for actually writing papers as nested, collapsible lists.

### Tips and tricks

A little trick: When you are unsure about notation, define latex commands for the mathematical symbols.

* Example: `\newcommand{\capShare}{\alpha}`. Then `y = A k^\capShare`.

Avoid literals in your text.

* Let your code write a latex preamble with statments like `\newcommand{\meanWage}{7.53}`.
* Then in the text: "the mean wage in the sample is \$\meanWage".
* That way, you don't have to manually update the numbers in the text. It's more robust.

### Tables ###

Don't write tables by hand. Let your code write them. It's faster and it avoids mistakes.

It is fairly easy to write basic `Latex` tables using code. I have `Matlab` code for this purpose in my [github](https://github.com/hendri54/) repo.

## Links ###

1. [Tips on Writing Economics Papers](http://www.bus.lsu.edu/hill/writing_economics_papers.htm) by R. Carter Hill (a collection of links)
2. [A Guide to Writing in Economics](http://lupus.econ.duke.edu/ecoteach/undergrad/manual.pdf) by P. Dudenhefer. Written for undergraduate writing, but also useful for PhD students.
3. [Writing Tips For Economics Research Papers](www.people.fas.harvard.edu/~pnikolov/resources/writingtips.pdf) by P. Nikilov.

--------