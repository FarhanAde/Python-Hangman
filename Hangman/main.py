from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.core.audio_output import SoundLoader

import random

# global variables
words = {5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[], 13:[], 14:[], 15:[]}
DATA_FILENAME = "CSVs/words.csv"
HANGMAN_PICS = ["images/Hangman_Picture1.png", "images/Hangman_Picture2.png", "images/Hangman_Picture3.png", "images/Hangman_Picture4.png", "images/Hangman_Picture5.png", "images/Hangman_Picture6.png"]
rawData = []
goalWord = ""
display = ""
totalScore = 0
length = 0
guessesLeft = 5
charsGuessed = ""
isGuessed = []

# global methods
# get data
def readData(fileName):
    global rawData
    file = open(fileName, "r")
    rawData = []
    for line in file:
        line = line.strip()
        line = line.split(", ")
        rawData += line
    return(rawData)

# add words to dictionary by length
def sortData(unsorted):
    global words
    for i in unsorted:
        lenList = words.get(len(i))
        lenList.append(i)
        words.update({len(i):lenList})

# generates random word to guess then loads it
def loadGuessWord():
    global goalWord
    global length
    possibleWords = words[length]
    lenPossWords = len(possibleWords)-1
    GWI = random.randint(0, lenPossWords)
    goalWord = possibleWords[GWI]

class HomeScreen(FloatLayout):
    def goToInstructions(self):
        game.screenManager.transition = SlideTransition(direction="left")
        game.screenManager.current = "Instructions"
    
    def goToWordChoice(self):
        game.screenManager.transition = SlideTransition(direction="left")
        game.screenManager.current = "Word Choice"

class InstructionScreen(FloatLayout):
    def returnHome(self):
        game.screenManager.transition = SlideTransition(direction="right")
        game.screenManager.current = "Home"

class WordChoiceScreen(FloatLayout):
    global readData
    global sortData
    global loadGuessWord

    def returnHome(self):
        game.screenManager.transition = SlideTransition(direction="right")
        game.screenManager.current = "Home"

    def goToPlayingScreen(self, int):
        global guessesLeft
        global length
        global display
        global isGuessed
        global charsGuessed
        
        display = int * "_"
        length = int
        guessesLeft = 5
        charsGuessed = ""
        isGuessed = []
        for i in range(length):
            isGuessed.append("not guessed")
        game.screenManager.transition = SlideTransition(direction="left")
        game.screenManager.current = "Playing"
        game.PlayingScreen.ids.guessesLeft.text = "[font=BazookaRegular]Lives Left:\n5[/font]"
        game.PlayingScreen.ids.display.text = f"[font=BazookaRegular]{display}[/font]"
        game.PlayingScreen.ids.theMan.source = "images/Hangman_Picture1.png"
        sortData(readData(DATA_FILENAME))
        loadGuessWord()

class PlayingScreen(FloatLayout):
    global goalWord
    charsGuessed = ""

    def returnToChoiceScreen(self):
        global guessesLeft
        game.screenManager.transition = SlideTransition(direction="right")
        game.screenManager.current = "Word Choice"
        guessesLeft = 5
    
    def goToGameEndScreen(self):
        game.screenManager.transition = SlideTransition(direction="left")
        game.screenManager.current = "Game Over"

    def submitGuess(self):
        global guessesLeft
        global charsGuessed
        global display
        guessChar = self.ids.guessID.text.lower()
        warning = Label(markup=True, color="red", text="[font=BazookaRegular]Please enter one letter to guess[/font]", size_hint = (.6, .1), pos_hint = {"x": .2, "y": .35})
        warning2 = Label(markup=True, color="green", text="[font=BazookaRegular]You've already guessed that letter[/font]", size_hint = (.6, .1), pos_hint = {"x": .2, "y": .35})
        warning4 = Label(markup=True, color="purple", text="[font=BazookaRegular]Try again![/font]", size_hint = (.6, .1), pos_hint = {"x": .2, "y": .35})
        if guessChar not in "qwertyuiopasdfghjklzxcvbnm" or len(self.guessChar.text) != 1:
            self.add_widget(warning)
            Clock.schedule_once(lambda dt: self.remove_widget(warning), 1)
        elif guessChar in charsGuessed:
            self.add_widget(warning2)
            Clock.schedule_once(lambda dt: self.remove_widget(warning2), 1)
        elif guessChar in goalWord:
            display = ""
            for i in range(len(goalWord)):
                if guessChar == goalWord[i]:
                    isGuessed[i] = "guessed"
            for i in range(len(isGuessed)):
                if isGuessed[i] == "not guessed":
                    display += "_"
                else:
                    display += goalWord[i]
            self.ids.display.text = f"[font=BazookaRegular]{display}[/font]"
            charsGuessed += guessChar
            if display == goalWord:
                sound = SoundLoader.load("audio/success-fanfare-trumpets-6185.mp3")
                if sound:
                    sound.volume = .4
                    sound.play()
                game.GameEndedScreen.ids.header.text = "[font=BazookaRegular]YOU WIN![/font]"
                game.GameEndedScreen.ids.header.color = "green"
                game.GameEndedScreen.ids.message.text = "[font=BazookaRegular]You successfully\nguessed the word[/font]"
                Clock.schedule_once(lambda dt: self.goToGameEndScreen(), 3.2)
                # self.goToGameEndScreen()
        else:
            self.add_widget(warning4)
            Clock.schedule_once(lambda dt: self.remove_widget(warning4), 1)
            guessesLeft -= 1
            self.ids.theMan.source = HANGMAN_PICS[(5-guessesLeft)]
            if guessesLeft == 0:
                sound = SoundLoader.load("audio/Voicy_Womp Womp Sound.mp3")
                if sound:
                    sound.volume = .4
                    sound.play()
                game.GameEndedScreen.ids.header.text = "[font=BazookaRegular]YOU LOSE![/font]"
                game.GameEndedScreen.ids.header.color = "red"
                game.GameEndedScreen.ids.message.text = f"[font=BazookaRegular]The correct word\nwas '{goalWord}'[/font]"
                Clock.schedule_once(lambda dt: self.goToGameEndScreen(), 2)
                # self.goToGameEndScreen()
            charsGuessed += guessChar
            self.ids.guessesLeft.text = f"[font=BazookaRegular]Lives Left:\n{guessesLeft}[/font]"
        self.ids.guessID.text = ""
        
class GameEndedScreen(FloatLayout):
    def returnHome(self):
        game.screenManager.transition = SlideTransition(direction="right")
        game.screenManager.current = "Home"
    
    def returnToChoiceScreen(self):
        global guessesLeft
        game.screenManager.transition = SlideTransition(direction="right")
        game.screenManager.current = "Word Choice"
        guessesLeft = 5

class Hangman(App):
    def build(self):
        Window.size = (480, 1067)
        self.screenManager = ScreenManager()

        self.HomeScreen = HomeScreen()
        screen = Screen(name="Home")
        screen.add_widget(self.HomeScreen)
        self.screenManager.add_widget(screen)

        self.InstructionScreen = InstructionScreen()
        screen = Screen(name="Instructions")
        screen.add_widget(self.InstructionScreen)
        self.screenManager.add_widget(screen)

        self.WordChoiceScreen = WordChoiceScreen()
        screen = Screen(name="Word Choice")
        screen.add_widget(self.WordChoiceScreen)
        self.screenManager.add_widget(screen)

        self.PlayingScreen = PlayingScreen()
        screen = Screen(name="Playing")
        screen.add_widget(self.PlayingScreen)
        self.screenManager.add_widget(screen)

        self.GameEndedScreen = GameEndedScreen()
        screen = Screen(name="Game Over")
        screen.add_widget(self.GameEndedScreen)
        self.screenManager.add_widget(screen)

        return self.screenManager

if __name__ == "__main__":
    game = Hangman()
    game.run()