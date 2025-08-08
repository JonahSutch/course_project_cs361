import random
import zmq

def opening_page():
    print("Welcome to the Song Playlist Creator and Recommender!")
    print("On this site you can add songs to a database for playlists "
    "and then use those songs for recommendations")
    while True:
        user_input = input("Type 'start' to begin or 'exit' to quit: ").strip().lower()
        if user_input == 'start':
            return True
        elif user_input == 'exit':
            print("Quitting the site.")
            return False
        else:
            print("Invalid input. Please type 'start' or 'exit'")


def welcome_page():
    print("\n=== Main Menu ===")
    print("1. Add a Song")
    print("2. Get a Recommendation")
    print("3. Info Page")
    print("4. Song Guesser Game")
    print("5. Exit the program")
   
    while True:
        choice = input("Enter the number of your choice (1-5): ").strip()
        if choice in {'1', '2', '3', '4', '5'}:
            return int(choice)
        else:
            print("Please enter 1, 2, 3, 4, or 5.")


def add_song():
    print("\n=== Add a Song ===")
    print("Enter song information below. Type 'back' at any prompt to return to the main menu.")
    print("The song will be added to the main database of songs and also the playlist you select")
    print("*note, you wont be able to change the info later*\n")

    song_name = input("Song name: ").strip()
    if song_name.lower() == 'back':
        return

    artist = input("Artist: ").strip()
    if artist.lower() == 'back':
        return

    genre = input("Genre: ").strip()
    if genre.lower() == 'back':
        return

    mood = input("Mood: ").strip()
    if mood.lower() == 'back':
        return
    
    playlist = input("Playlist: ").strip()
    if playlist.lower() == 'back':
        return

    entry = f"{song_name}_{artist}_{genre}_{mood}\n"
    try:
        with open("songs", "a", encoding="utf-8") as file:
            file.write(entry)
        print(f"\n '{song_name}' by {artist} added to songs database\n")

    except Exception as e:
        print(f"Error writing to file: {e}")

    try:
        with open(playlist, "a", encoding="utf-8") as file:
            file.write(entry)
        print(f"\n '{song_name}' by {artist} added to your playlist!\n")

    except Exception as e:
        print(f"Error writing to file: {e}")


def info_page():
    print("\n=== Info Page ===")
    print("Site created by Jonah Sutch")
    print("Email – sutchj@oregonstate.edu")
    print("Most recent update {Jul 25 2025}\n")
    print("On this site you can add songs to the library and playlists.")
    print("You then can use the library you make to get a random")
    print("song recommendation by mood or genre. To start type")
    print("back and then select an action, either to add a song or get ")
    print("a recommendation.")
    print("The song guesser is a game you can play. When you enter the song guesser")
    print("it will randomly pick a song from the general library and then quix you on one of the parts")
    response = input("\nEnter 'back' to go back to the menu: ").strip()
    if response == 'back':
        return


def get_recommendation():
    print("\n=== Get a Recommendation ===")
    print("Would you like a recommendation by genre or mood?")
    
    while True:
        answer = input("Type 'genre' or 'mood' (or 'back' to return): ").strip().lower()
        if answer in {'genre', 'mood'}:
            break
        elif answer == 'back':
            return
        else:
            print("Invalid input. Please type 'genre', 'mood', or 'back': ")
    
    while True:
        source = input("Pick if you want it from 'general' library or 'playlist'? Or select 'back'").strip().lower()
        if source == 'general':
            file_name = "songs"
            break
        elif source == 'playlist':
            file_name = input("Enter the playlist name (or 'back' to return): ").strip()
            if file_name.lower() == 'back':
                return
            break
        elif source == 'back':
            return
        else:
            print("Please type 'general' or 'playlist' or 'back'.")
    
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error getting playlist '{file_name}': {e}")
        return

    if not lines:
        print(f"No songs found in '{file_name}'.")
        return

    index = {'genre': 2, 'mood': 3}[answer]
    options = set()
    songs = []

    for line in lines:
        parts = line.strip().split('_')
        if len(parts) == 4:
            songs.append(parts)
            options.add(parts[index])

    if not options:
        print(f"No {answer}s found in '{file_name}'.")
        return

    print(f"\nAvailable {answer}s:")
    options = sorted(options)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    
    while True:
        try:
            choice = int(input(f"\nSelect a {answer} (1-{len(options)}): ").strip())
            if 1 <= choice <= len(options):
                selected = options[choice - 1]
                break
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a number.")

    matches = [s for s in songs if s[index] == selected]

    if matches:
        song = random.choice(matches)
        print(f"\n🎵 Recommendation: '{song[0]}' by {song[1]} — {song[2]} / {song[3]}")
    else:
        print(f"No songs found with that {answer}.")


def song_guesser():
    print("\n=== Song Guesser Game ===")
    print("You’ll be given a song with one detail missing (name, artist, genre, or mood).")
    print("Try to guess the missing detail!")

    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        socket.send_string("start")
        response = socket.recv_json()

        print("\n" + response["question"])

        user_guess = input(f"\nYour guess for the missing {response['missing']}: ").strip()
        socket.send_string(f"guess:{user_guess}")
        result = socket.recv_string()

        if result == "true":
            print("Correct!\n")
        else:
            print(f"Incorrect. The correct {response['missing']} was: {response['answer']}\n")

    except Exception as e:
        print(f"Error communicating with song guesser microservice: {e}")
    return


def main():
    if not opening_page():
        return
    
    while True:
        selection = welcome_page()
        if selection == 1:
            add_song()
        elif selection == 2:
            get_recommendation()
        elif selection == 3:
            info_page()
        elif selection == 4:
            song_guesser()
        elif selection == 5:
            print("Exiting")
            return

if __name__ == "__main__":
    main()
