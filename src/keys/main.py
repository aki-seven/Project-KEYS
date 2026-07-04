import argparse
import sys
import random
import time
from keys.core.bootstrap import validate_dependencies
from rich import print
from rich.live import Live
from rich.text import Text
from rich.console import Console

def print_banner():
    

    # logo = [
    # # r"""
    # # ██╗ █████╗ ██╗
    # # ██║██╔══██╗██║
    # # ██║███████║██║
    # # ██║██╔══██║██║
    # # ██║██║  ██║██║
    # # ╚═╝╚═╝  ╚═╝╚═╝
    # # """,
    # r"""

    #     ██╗  ██╗ ████████╗ ██╗   ██╗ ███████╗
    #     ██║ ██╔╝ ██╔═════╝ ╚██╗ ██╔╝ ██╔════╝
    #     █████╔╝  ██████╗    ╚████╔╝  ███████╗
    #     ██╔═██╗  ██╔═══╝     ╚██╔╝   ╚════██║
    #     ██║  ██╗ ████████╗    ██║    ███████║
    #     ╚═╝  ╚═╝ ╚═══════╝    ╚═╝    ╚══════╝

    # """,
    # r"""

    #     ░██╗░░██╗ ░███████╗ ░██╗░░░██╗ ░███████╗
    #     ░██║░██╔╝ ░██╔════╝ ╚░██╗░██╔╝ ░██╔════╝
    #     ░█████╔╝░ ░█████╗░░ ░░╚████╔╝░ ░███████╗
    #     ░██╔░██╗░ ░██╔══╝░░ ░░░╚██╔╝░░ ╚═════██║
    #     ░██║░░██╗ ░███████╗ ░░░░██║░░░ ░███████║
    #     ░╚═╝░░╚═╝ ░╚══════╝ ░░░░╚═╝░░░ ╚═══════╝

    # """
    # ]

    BANNERS = [
    r"""
                                            .........    .::-------::.             
                                        ...............---::::--=++++==-.         
                                        .:..............:::          .:-=+==:       
                                    ::.:.::............::             .-=+=      
                                    .:.::-:...........::...              :=+-     
                                    .:-::-=: .........==+##-..              =+-     
                            ....::-==--#+..........:#*==#+...           .-==      
                    ....:::::::::::::=%= .........:-##*+=-::.      ..:--:.       
                ......::::::::::::::::--*@+ .............=##*+=====----::..         
        .:....::::::::::::::::::::::::+#=....  .........:+++*+:::...              
        ::::::::::...:::::...      ..   ...:..              .:.                    
        =-:::::.......                 ...:....             .                      
        .....                     ............           .                       
                                ...........:. .....                              
                                ............:.                                     
                            ..............                           ██╗  ██╗ ████████╗ ██╗   ██╗ ███████╗          
                            ............                             ██║ ██╔╝ ██╔═════╝ ╚██╗ ██╔╝ ██╔════╝           
                        ....::.......                                █████╔╝  ██████╗    ╚████╔╝  ███████╗           
                        ....::..... .                                ██╔═██╗  ██╔═══╝     ╚██╔╝   ╚════██║           
                    :..:::::....                                     ██║  ██╗ ████████╗    ██║    ███████║           
                    ::::::...                                        ╚═╝  ╚═╝ ╚═══════╝    ╚═╝    ╚══════╝           
                    =:.....                                                           
    """,
    r"""
                                            ,,,,,,,,,    ..::^^^^^^^::.             
                                        ,,,,,,,,,,,,,,,,^^::::^^=****==^.         
                                        .:,,,,,,,,,,,,,,,:~~          .:^=*==:       
                                    ::.:.~:,,,,,,,,,:~,,,             .^=*=      
                                    .:.:^~:,,,,,,,,,,:~,,,              :=*^     
                                    .:^:^=:. ,,,,,,,,,==+%%^,,              =*^     
                            ,,,,.:^==^^%%,,,,,,,,,,,:#*==%%,,,           .^==      
                    ,,,,:::::::::::^=%= ,,,,,,,,,,,^^##*+=^::,      ,,:^~:.       
                ,,,,,,::::::::::::::::^+@+ ,,,,,,,,,,,,,=##*+=====^^^^::,,         
        .:,,,::::::::::::::::::::::::+#=,,,,  ,,,,,,,,,:+++*+:::,,,              
        ::::::::::,,,:::::,,,      ,,   ,,,~,,              .:.                    
        =^:::::,,,,,,,                 ,,,~,,,,             .                      
        ,,,,,                     ,,,,,,,,,,,,           .                       
                                ,,,,,,,,,,,~. ,,,,,                              
                                ,,,,,,,,,,,,~.                                     
                            ,,,,,,,,,,,,,                            ░██╗░░██╗ ░███████╗ ░██╗░░░██╗ ░███████╗
                            ,,,,,,,,,,,,                             ░██║░██╔╝ ░██╔════╝ ╚░██╗░██╔╝ ░██╔════╝         
                        ,,,,::~,,,,,                                 ░█████╔╝░ ░█████╗░░ ░░╚████╔╝░ ░███████╗
                        ,,,,::~,,,,, ,                               ░██╔░██╗░ ░██╔══╝░░ ░░░╚██╔╝░░ ╚═════██║
                    :,,:::::,,,,                                     ░██║░░██╗ ░███████╗ ░░░░██║░░░ ░███████║          
                    ::::::,,,                                        ░╚═╝░░╚═╝ ░╚══════╝ ░░░░╚═╝░░░ ╚═══════╝          
                    =:,,,,,                                                       
    """
    ]

    banner = random.choice(BANNERS)
    # logo_choice = random.choice(logo)

    keys = banner
    
    console = Console()
    colors = [
        "#442200",
        "#663300",
        "#995500",
        "#cc7700",
        "#ff8800"
    ]

    rendered_lines = []

    with Live(refresh_per_second=30, console=console) as live:

        for line in keys.splitlines():

            # preserve spacing
            if not line.strip():
                rendered_lines.append(Text(""))
                continue

            # fade animation
            for color in colors:

                temp = rendered_lines + [
                    Text(line, style=f"bold {color}")
                ]

                live.update(
                    Text("\n").join(temp)
                )

                time.sleep(0.03)

            # final stable color
            rendered_lines.append(
                Text(line, style="bold #ff8800")
            )

            live.update(
                Text("\n").join(rendered_lines)
            )

    console.print("[cyan]Version:[/cyan] v1.0")
    console.print("[cyan]Author:[/cyan] aki")
    console.print("[cyan]Framework:[/cyan] Initial Access Intelligence (IAI)")
    console.print()

    time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description="IAI - Professional Reconnaissance Framework")
    parser.add_argument("target", help="Target IP or Domain (e.g. 10.10.10.10 or example.com)")
    
    args = parser.parse_args()
    
    # Banner
    print_banner()


    # 1. Dependency Validation
    try:
        validate_dependencies()
    except SystemExit:
        sys.exit(1)

    # 2. target Validation
    try:
        if not args.target:
            print("[!] Error: Target not specified. Run with -h for help.")
            sys.exit(1)
    except SystemExit:
        sys.exit(1)


    # 3. Launch TUI Runtime
    # Import TUI components only after validating dependencies
    from keys.tui.app import IAIApp
    
    app = IAIApp(target=args.target)
    app.run()

if __name__ == "__main__":
    main()
