Cellular Automata Toy
=====================

Introduction
------------


The Cellular Automata Toy (CAT) is a very basic framework for
experimenting with and prototyping 2 dimensional Cellular Automata
models.

It provides a graphical display of the CA in the form of
a grid, an interface to manipulate the state and step through
computations and handles the connections between cells (providing each
cell with a list of the values in its neighboring cells). It just
leaves the actual specification of transition rules to the user
in the form of a textbox that they can enter small bits of python
code into.


It is intended only for experimentation, exploration, and
demonstration of CA concepts. It is not intended to be high
performance. 

Install
-------

you must have Python 2.2+ installed 
on your system to run the program. If python didn't come with it, you
will also need the Tkinter library. Python's NumPy and Imaging
libraries are also required. 

On Ubuntu, you can do:

    $ sudo aptitude install python-imaging python-imaging-tk python-numeric

To install the necessary libraries.

Tutorial
--------

run cat by typing `python cat.py` at a command prompt (and from within
the folder that `cat.py` is in). you should see a window like:

!https://github.com/thraxil/cat/raw/master/cat1.png

Each cell has 8 bits of state (ie, 256 different possible states).
CAT displays the state of each cell on the grid by mapping it to a
shade of gray with 0 = black and 255 = white. when CAT is started, it
sets each cell on the grid to a random value.

Clicking the 'clear' button will set bits of all cells on the grid to
0 (they will display as black). clicking the 'random' button will set
all bits of all cells on the grid to random values between 0 and
255. clicking the 'boolean' button will force all the bits of each
individual cell to the value of the most significant bit for that
cell. in other words, it removes the grayscale and rounds each cell up
to 255 (white) or down to 0 (black). right now, clicking the 'step'
button should have no noticable effect.

Clicking on any cell on the grid at any time will toggle the value of
each bit of that cell. what that essentially does is subtract the
current value of the cell from 255. so if the cell is black (a value
of zero), clicking on it will set it to 255 - 0 = 255 (white). if the
cell is white (a value of 255), clicking on it will set it to 255 -
255 = 0 (black).


To actually do anything useful with CAT, you must enter some
python code into the textbox below the grid. this document assumes that the 
reader is familiar with basic python programming and simple Object Oriented
programming concepts. It would also be very useful for the reader to
familiarize themselves somewhat with the workings of the Numeric
library but isn't necessary to complete this tutorial.


When you click the 'step' button, CAT executes the code that you've 
entered into the text box once for each cell of the grid, then displays
the new state of the grid.

to get a feel for how this works, enter the following code
into the text box:

    c = on

when you click 'step', this should set every cell on
the grid to 255 (white). it should 
look like:

!https://github.com/thraxil/cat/raw/master/cat2.png

similarly, entering:

    c = off

should have the opposite effect, turning every cell off (the same as
hitting the 'clear' button):

!https://github.com/thraxil/cat/raw/master/cat3.png

`c` is a variable (actually a Numeric array, but for now we'll
pretend that it's just a simple variable. later on we'll take a closer
look at it.) that represents the state of
the current cell (`c` really stands for 'center'). in addition to `c`,
CAT gives you access to variables called
`n`,`s`,`e`,`w`,`nw`,`ne`,`sw`, and `se` that represent the state of
the cell to the
north of the current cell, the state of the cell to the south of the
current cell, etc. `c` is really the only one that you'll be modifying
though (if you modify any of the other variables, they'll be ignored).
there are also some special variables made available: `off` and `on`
are constants that correspond to all bits off or all bits on
respectively. `m_cnt` and `vn_cnt` are the number of Moore neighbors
(the Moore neighborhood includes all 8 immediate neighbors of the cell)
and Von Neuman neighbors (the Von Neuman neighborhood doesn't include
the diagonal neighbors ne, nw, se, or sw). `m_total` and `vn_total`
are the respective counts plus the value of the center. 


to get a feel for the relationships between the variables try
something like:

     c = n

when you hit `start`, you should see everything shift steadily
south. (unless the grid is uniform, in which case things are still
working but obviously you won't see anything). this is because every
cell is being replaced by the value of its northern neighbor. try
setting c to the value of some of the other neighbors instead and make
sure that it does what you would expect.


Most of the more interesting CA rules you'll encounter will
require bitwise logical operations. these include `~` for negation,
`&` for AND, `|` for OR, and `^` for XOR. if you don't know what
those operations are, you'll have to consult your favorite python
reference, symbolic logic text, bother your friendly neighborhood
electrical engineer, or just experiment and figure them out for
yourself. you'll also probably use `==` and `!=` for comparisons.

the classic example of Cellular Automata is Conway's Game of Life.
it has 4 very simple rules:

* if a cell has 0 or 1 neighbors, it dies from isolation
* if a cell has 4 or more neighbors, it dies from overcrowding
* if a dead cell has exactly 3 neighbors, it comes to life
* otherwise, it stays in whatever state it was in

Now to see how those logical operations are put to use, 
we'll convert those rules to the following python code (you'll
probably want to randomize the grid, then hit the 'boolean' button
before running this code):

    alive = (c == 1) &  ((m_cnt == 2) | (m_cnt == 3))
    born  = (m_cnt == 3) & (c == 0)
    c   = alive | born

the first line sets a new variable `alive` to '1' if the cell was
already alive and has the right number of neighbors to stay
alive. otherwise it is set to '0'. (remember that the 'm_cnt' variable
is the total number of neighbors in the cell's Moore
neighborhood). the second line sets another variable 'born' to '1' if
it was previously dead but has exactly 3 neighbors. the last line just
updates the cell's value. the OR operator sets the value to '1' if
either the cell is still alive, or was just born. if neither is the
case, the cell is set to '0'.

It is also important to notice how CAT handles cells on the edge of
the grid. the edges of the grid wrap around. the upper neighbors
of cells on the top row of the grid are actually the corresponding
cells on the bottom row of the grid and vice versa. you can think 
of the grid as the surface of a toroid.

The Game of Life is a very simple CA that only requires two
states 'alive' and 'dead'. what happens when we want to write CA rules
that need more than just two states? CAT makes it fairly
straightforward, but first we'll need to take a closer look at what
those variables really are.

As i mentioned earlier, the variables like `c`, `n`, etc.  are
actually Numeric arrays, rather than plain python variables. it's
actually even more complicated than that; they are really
3-dimensional Numeric arrays. python's Numeric library does a
fantastic job of letting you work with multidimensional arrays
pretending that they are just regular variables, but eventually,
you'll need to get under the hood to do anything really fancy with
them. 

Each variable is a stack of two dimensional grids of bits. we'll
call each of the two-dimensional grids a 'bit plane'. there are eight
bit planes for each variable. each bit-plane has as many rows and
columns as CAT's main grid. for the purposes of writing CA rules,
you'll almost never want to access individual cells or rows or columns
of a bit-plane, but you probably will want to access the individual
bit-planes now and then. luckily, this is easy:

    c[7] = 1

that command sets the most significant bit (in position 7; the
least significant bit is in position 0) of each cell to '1'. if you
run it on a randomized grid, you'll notice that it gets
lighter. setting the next bit, c[6] to 1 will make it somewhat lighter
still. 

at this point, if you understand how to work with Numeric arrays, you
should be all set. otherwise, you're probably still confused and have
no choice but to go read up on Numeric until things become clear.

CAT comes with a number of example rules to get you started in
`numeric_examples.py`.


Limitations
-----------

Since CAT is a very general framework and is only
intended for experimentation, it has some pretty serious limitations.

secondly, it is not at all efficient. since any algorithm can
be plugged in for the computation step, there are no cases that can 
safely be optimized away (eg, dedicated implementation of the Game of Life
will usually only bother calculating the new state for cells that are
in 'active' neighborhoods and won't bother at all with large swaths of 
dead cells since there's no chance that they'll change). CAT has to 
perform the calculation for every cell every single time through. CAT also
aims to have a conceptual model that is easy to grasp rather than
something more difficult that might be more computationally efficient.
as a result, you'll probably find that CAT gets quite slow on large
grids.


Acknowledgements
----------------

CAT's design is based heavily on the CAM-6 machine
developed at the MIT Laboratory for Computer Science  and described in
the book [Cellular Automata Machines: A New Environment
for Modeling](http://www.amazon.com/exec/obidos/tg/detail/-/0262200600/) by Toffoli and Margolus.
It was written by Anders Pearson for the [Columbia Center for New Media
Teaching and Learning](http://ccnmtl.columbia.edu/) as part of the OPTIMUS project.
Additional input and suggestions from [Don Hopkins](http://www.donhopkins.com/).

TODO
----

* colormaps so it isn't restricted to greyscale
* better drawing tools for manually manipulating things.
* more example rules and documentation
* convert to pygame?
* more user configurability. ie, menus to change size of grid,
number of bit-planes, etc.
* make standalone executable version for windows
* more aggressive caching and table-building
* can I offload processing to a GPU?
* make better use of multi-core processors?
