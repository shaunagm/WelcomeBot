# WelcomeBot and Automated Testing

In order to quickly and easily test changes to WelcomeBot, we've created an automated test suite using Python's unittests.  This tutorial will cover the concepts necessary to use our suite, but unit testing is an important concept worth checking out in its own right.  Here are some great resources you might want to check out:

* [Getting Started Testing](https://www.youtube.com/watch?v=FxSsnHeWQBY), a talk by [Ned Batchelder](http://nedbatchelder.com/) at PyCon 2014
* [Understanding Unit Testing](http://www.jeffknupp.com/blog/2013/12/09/improve-your-python-understanding-unit-testing/) by Jeff Knupp
* [Unit Test Introduction](http://pythontesting.net/framework/unittest/unittest-introduction/) by Brian Okken

## Tutorial

[unittests](https://docs.python.org/2/library/unittest.html) is a Python library (part of the [standard library](https://docs.python.org/2/library/)) designed to help people automate testing of their code.  We use it here to create a file of tests, `test_bot.py`, which can be run quickly after setting up the bot on a new machine or making changes to the code, to see if the bot is still working as specified.

There are a few key concepts that unittests introduces.

### TestCase classes

All unit tests must be grouped within a class.  This class is a __child__ of the unittest class TestCase.  This means that it inherits all of the functions and attributes of TestCase.  (See [chapter 44 of Learn Python the Hard Way](http://learnpythonthehardway.org/book/ex44.html) for more details on inheritance in Python.)

In `test_bot.py`, the first test class we create is for testing the object bot:

    class TestBotClass(unittest.TestCase):

As you can see, it is the child of parent `unittest.TestCase`.  This means it inherits some important methods.  What are they?

#### setUp and tearDown methods

As we are writing an awful lot of tests, it is inefficient and unsightly to do all of the setup and cleanup for every single test.  For each class, we can specify what needs to be done to setup and cleanup after each test.  For clarity's sake, let's rephrase and repeat that.  For each test method, `setUp()` then the test method and then `tearDown()` will be run, in that order.

In our first class, our setup process involves instantiating our bot class.  We do this by calling `botcode.Bot()`, where `botcode` is our name for the code imported from `bot.py`:

    def setUp(self):
        self.bot = botcode.Bot()

Our `tearDown()` method is slightly more complex.  We have a test version of our nicknames file, `nicks.csv`, called `test_nicks.csv`.  Because the `bot` class alters `nicks.csv`, our `TestBotClass` needs to alter `test_nicks.csv`.  When the test is over, `tearDown()` replaces the new `test_nicks.csv` with the original version:

     with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

Other classes may have different content within `setUp()` and `tearDown()`.  In some rare cases there is no setup and/or cleanup needed, in which case one or both of these methods are not used.

#### Assert methods

There are a number of methods that allow you to compare two results.  These methods raise an error if the assertion is not met.  There is a default behavior for the error, as well as an optional message parameter that allows us to specify the error message on a test-by-test basis as needed.  Let's look at an example:

    def test_add_nick_to_list(self):
        self.bot.known_nicks = [['Fluffy'], ['Spot']]
        self.bot.add_known_nick('Roger')
        self.assertEqual(self.bot.known_nicks,[['Fluffy'], ['Spot'], ['Roger']])

With this test, we are checking whether the function add_known_nick() is working as expected.  We start by specifying a set of already known nicknames, `['Fluffy']` and `['Spot']`, in the format used by the bot (a list of lists).  We then call the function we're testing with some sample input, `Roger`.  Finally, we call the inherited method, `assertEqual`.  We give it two things to compare: the result of the two previous lines (`self.bot.known_nicks`) and what we expect the result to be (`[['Fluffy'], ['Spot'], ['Roger']]`).

There are many different kinds of assert methods, which you can see listed [here](https://docs.python.org/2/library/unittest.html#unittest.TestCase.assertEqual).  Another example, from later in `test_bot.py`, is a bit more complex:

    def test_newcomer_init_born(self):
        newComer = botcode.NewComer('Baby', botcode.Bot())
        time.sleep(0.01)
        self.assertAlmostEqual(newComer.born, time.time() - .01, places=2)

Here, we're trying to test whether the bot's timing is correct.  This is important, as the bot welcomes people based on how much time has passed since they arrived in the channel.  Because python's time function `time.time()` returns a precise floating point number, the times we are comparing may not be exactly equal.  But we don't really care about hundredths or thousands of a second here, since we're dealing with human patiences - at most we care about tenths of seconds, and probably not even that.  So we can use `assertAlmostEqual`, which allows us to specify how equal the numbers should be via the argument `places`.  Here, we specify that it only needs to be equal to two decimal places.

### Other classes and functions

In addition to the testCase classes, there's a few other functions, classes and statements in `test_bot.py`.  What are they?

#### fake_ircsock and fake_irc_start

This class and function are "mock" objects that allow us to test the parts of our code that involve using the IRC protocol without actually connecting to IRC.  It's somewhat of a hacky solution, but we're using it for now.  To see how it works, let's first look at the real ircstart function in `bot.py`:

    def irc_start(): # pragma: no cover  (this excludes this function from testing)
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ircsock.connect((server, 6667))  # Here we connect to server using port 6667.
        return ircsock

As you can see in the comment, this function is excluded from testing.  It's actually excluded by virtue of not being called in `test_bot.py` but the statement `pragma: no cover` excludes it from the [coverage tool](http://nedbatchelder.com/code/coverage/) as well (see more [below](#Using coverage to inspect tests)).  In any case, the real `ircstart()` uses the socket library to establish a connection with the IRC server and returns all details of that connection in an object called `ircsock`.

When we looked at how our various functions use `ircsock`, we decided that the main thing we wanted to test is whether or not it was sending messages, and what those messages were.  So our fake ircsock has functions which keep track of messages:

    def __init__(self):
        self.sent_messages = []
    
    def send(self, msg):
        self.sent_messages.append(msg)

    def sent_message(self):
        return self.sent_messages[-1]
        
    def has_sent_message(self):
        if self.sent_messages:
            return True
        else:
            return False

We can see this class being used when we test the bot's ability to say hello:

    def test_hello(self):
        botcode.message_response(self.bot,"PRIVMSG sup WelcomeBot2","Shauna", ircsock=self.ircsock)
        self.assertTrue(self.ircsock.has_sent_message())

The function `fake_irc_start()` simply creates a fake_ircsock object which can be called by tests that need it:

    def fake_irc_start():
        ircsock = fake_ircsock()
        return ircsock   

#### if __name__ == '__main__`

Finally, at the very bottom of the file is a little piece of code:

    if __name__ == '__main__':
        unittest.main()

All of the above code is in the form of import statements, classes and methods.  In order to actually run the script, we need this little line of code.  `if __name__ == '__main__:` translates to "if this module is being run directly, and not called/imported from another file".  You can learn more about the terminology [here](http://www.diveintopython3.net/your-first-python-program.html#runningscripts).

### Running and Interpreting the Tests

As the main readme explains, you can run the test suite with this command:

    python -m unittest test_bot

Let's take a look at some output you might see.  First, there is a series of dots and letters:

    ...........F.FF.....EE.......F  

Each dot or letter refers to a specific test being run.  An F means that the test failed.  An E means that there was an error.  

Let's take a closer look at what a failed test looks like.  I'm going to generate an error by altering `test_custom_wait_time()` to specify the wrong amount in `assertEqual()`.  You can cause similar test failures by changing assertions in `test_bot.py`.  

    def test_custom_wait_time(self):
        bot = botcode.Bot(wait_time=30)
        self.assertEqual(bot.wait_time, 35) # changed 30 to 35

When I do this, I see the following after running the unittests:

    ======================================================================
    FAIL: test_custom_wait_time (test_bot.TestBotClass)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "test_bot.py", line 52, in test_custom_wait_time
        self.assertEqual(bot.wait_time, 35)
    AssertionError: 30 != 35

This message tells me the test that has failed, the line in which it has failed, and, conveniently, the two values that end up being compared.  Using this information, I need to decide whether there is a problem with the test or a problem with the code being tested.  In this instance, I know it is a problem with the test, and I can change it back.  A successful test will not produce any special output.

Different types of failures will give different output of varying helpfulness.  If we had specified any custom error messages with the parameter `msg` we might see that here, but we haven't used that feature in our test suite so far.

#### Using coverage to inspect tests

If you want to expand the tests to cover a new piece of code -- either code you have written, or that someone else has - you might find [Coverage](http://nedbatchelder.com/code/coverage/) to be a useful tool.  After installing coverage, you can run it, either in a virtual environment:

    ./bin/coverage run test_bot.py 

Or not in a virtual environment:

    coverage run test_bot.py

This will generate an html file which can be found by opening `htmlcov/index.html`.  This file gives you a report on the percentage of code covered by tests.  If you click the file being tested (not the test file, which should be covered 100%) you'll see a handy color-coded copy of the file indicated what is covered and what isn't.  Each statement is either covered ("run"), not covered ("missing") or excluded.  Excluded statements are excluded via the comment `pragma: no cover`, which we've used for WelcomeBot to ignore code interfacing with the socket library, as we're not sure how to test that yet.

## Conclusion

That concludes our documentation/tutorial on how we use unit tests.  Please feel free to submit questions or corrections via the issue tracker or IRC, and to make corrections via pull request.
