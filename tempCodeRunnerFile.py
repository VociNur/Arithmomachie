
            # self.detect_siege 1000 + 20s
            aim_attacks = self.get_attacks_with_aim_shooter() + self.detect_siege()

            available_aim_attacks = aim_attacks
            for no in pre_aim_attacks:
                if no in aim_attacks:
                    available_aim_attacks.remove(no)
                
            # for i in available_aim_attacks:
            #    print("AIMSHOOTER detects ", self.turn, ": ", str(i))

            self.game_attacks.append([])
            self.game_attacks[self.turn] = available_aim_attacks
            self.execute_all_attacks(available_aim_attacks)

            
            self.check_end() # moyen, +100sec/1000 exe par boucle
            self.end_turn()

        # print_board(self.board)
        self.is_finished = self.turn == self.max_turn
        if SHOW_PRINT:
            print(self.turn, self.max_turn)
            print(f"Finished: {self.is_finished}")
        if SHOW_PRINT:
            print("Fin en", self.turn, "tours")
        self.time_exe = time.time() - self.start_time
        
        print(f'Temps d\'exécution : {self.time_exe:.3}s')
        if SHOW_PRINT:
            print("Coups joués ", self.turn)
            print("nbr_coups", nbr_coups / self.turn)
        if view:
            self.show_game()


def find_win():
    while True:
        game = Game()
        if game.winner != -1:
            game.show_game()
            i = input("Another ?")
            if len(i) > 0:
                break


def launch_games(number, must_be_completed = False):
    c = 0
    for i in range(number):
        game = Game()
        