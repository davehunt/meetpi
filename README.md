# meetpi

## Introduction

In the 10+ years I've been working from home, I've found the most challenging times are when my kids aren't at school and I need to be in a meeting. I have a door hanger that I can flip, which lets everyone in the house know to keep the noise down, but wouldn't it be cool if I could have a bright status light that integrates directly with my calendar?

meetpi is a [Raspberry Pi](https://www.raspberrypi.org/) project that uses a [Blinkt!](https://shop.pimoroni.com/products/blinkt) RGB LED indicator to show current availability for a given Google Calendar. If an event is in progress with the user listed as an attendee

## Usage

The easiest way to run meetpi is to use [poetry](https://python-poetry.org/), which manages the virtual environment and dependencies. You can install poetry by following this [installation guide](https://python-poetry.org/docs/#installation).

Once you have poetry you will need to create the virtual environment and install the dependencies by running:

```
poetry install
```

You will need to tell meetpi which calendar to check for your availability. To find out your calendar ID follow these steps:

* Open [Google Calendar](https://calendar.google.com/) in your web browser.
* Locate your list of calendars and identify the one you want to use.
* Hover over the calendar and click the three vertical dots to open the calendar options.
* From the options menu click **Settings and sharing**.
* A new page will open. You'll find the **Calendar ID** under the **Integrate calendar** section.

Finally, you will need to create a project within the [Google Developers Console](https://console.developers.google.com/) to use the Calendar API. When you run meetpi for the first time you'll be prompted to authenticate. Once you provide the token it will be saved for future use.

Once you have poetry and your calendar ID, run the following command to start meetpi (using your actual calendar ID of course):

```
poetry run python meetpi/meetpi.py calendar@google.com
```

The first time you run meetpi it will ask you to authenticate with

There are some additional configuration options such as the brightness and query delay. To find out how to use these run `poetry run python meetpi/meetpi.py --help`.

## Development

If you're interested in hacking on meetpi, you can run the tests using `poetry run pytest`. If you want to contribute back, please feel free to include tests before [opening a pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests).

## Future

Here are a few ideas of things I might add in the future:

### Alternative display modes

Currently the pixels on the Blinkt! are either all red (busy), green (free), or off (out of office). An enhancement could be to use each pixel to represent an event on the calendar. The current event could pulse red to show I'm busy, and go green when it's over. This would answer the common question I get of "do you have any more meetings today?"

### Audio feedback

Sometimes the bright red light isn't enough, so I've considered adding a way to monitor the sound level and if it gets loud make a noise to signal that a meeting is in progress. I could also signal the start of a meeting.

### Configurable office hours

These don't change often, but it might be nice to have variable office hours based on the day.