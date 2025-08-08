import zmq # type: ignore
import random

# Constants
COLUMNS = ["name", "artist", "genre", "mood"]

def load_songs(filename="songs"):
    songs = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split('_')
            if len(parts) == 4:
                song = dict(zip(COLUMNS, parts))
                songs.append(song)
    return songs

def main():
    # Setup ZeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP = replies to requests
    socket.bind("tcp://*:5555")

    songs = load_songs()

    print("Song Guesser Microservice ready...")

    while True:
        request = socket.recv_string()

        if request == "start":
            song = random.choice(songs)
            hidden_key = random.choice(COLUMNS)
            correct_answer = song[hidden_key]

            # Mask the field to guess
            hint = song.copy()
            hint[hidden_key] = "???"

            message = (
                f"Guess the {hidden_key}!\n"
                f"Song: {hint['name']}\n"
                f"Artist: {hint['artist']}\n"
                f"Genre: {hint['genre']}\n"
                f"Mood: {hint['mood']}"
            )

            socket.send_json({
                "question": message,
                "missing": hidden_key,
                "answer": correct_answer
            })

        elif request.startswith("guess:"):
            user_guess = request.split("guess:", 1)[1].strip()
            result = (user_guess.lower() == correct_answer.lower())
            socket.send_string("true" if result else "false")

if __name__ == "__main__":
    main()