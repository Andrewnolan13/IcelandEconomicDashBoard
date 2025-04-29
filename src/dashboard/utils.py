def toggle_play_button(n_clicks:int)->tuple[str,bool,bool]:
    playPause = "Pause" if n_clicks % 2 == 1 else "Play"
    disabled = True if playPause == "Play" else False
    return (playPause,
            disabled, 
            not disabled # disable the other interval to reduce load
            )

def play_slider(playPause:str, value:int, n_intervals:int)->int:
    if playPause == "Play":
        return value
    else:
        return value + 1 if value+1 <= 2025 else 1850   