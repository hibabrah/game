# game
import tkinter as tk
from tkinter import messagebox
import random
from functools import partial
from itertools import combinations

class ChkobbaGame:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        """Initialize or reset the game state"""
        self.deck = self.create_deck()
        random.shuffle(self.deck)
        self.player_hand = []
        self.computer_hand = []
        self.table_cards = []
        self.player_collected = []
        self.computer_collected = []
        self.last_capturer = None
        self.deal_initial_cards()
        self.current_player = 'player'  # Player starts first
    
    def create_deck(self):
        """Create a 40-card deck (1-10 in four suits)"""
        return [(value, suit) for value in range(1, 11) 
                for suit in ['♠', '♥', '♦', '♣']]
    
    def deal_initial_cards(self):
        """Deal initial cards to players and table"""
        if len(self.deck) >= 10:  # Enough cards for initial deal
            self.player_hand = [self.deck.pop() for _ in range(3)]
            self.computer_hand = [self.deck.pop() for _ in range(3)]
            self.table_cards = [self.deck.pop() for _ in range(4)]
    
    def deal_additional_cards(self):
        """Deal new cards when hands are empty"""
        if not self.player_hand and not self.computer_hand and self.deck:
            cards_to_deal = min(3, len(self.deck))
            self.player_hand = [self.deck.pop() for _ in range(cards_to_deal)]
            self.computer_hand = [self.deck.pop() for _ in range(cards_to_deal)]
    
    def card_value(self, card):
        """Get the numeric value of a card"""
        return card[0]
    
    def card_suit(self, card):
        """Get the suit of a card"""
        return card[1]
    
    def format_card(self, card):
        """Format card for display"""
        return f"{card[0]}{card[1]}"
    
    def find_valid_captures(self, card, table):
        """Find all possible capture combinations for a played card"""
        captures = []
        target_value = self.card_value(card)
        table_values = [self.card_value(c) for c in table]
        
        # Check for single card capture
        for i, t_card in enumerate(table):
            if self.card_value(t_card) == target_value:
                captures.append([t_card])
        
        # Check for multi-card captures (sum of values)
        for r in range(2, len(table) + 1):
            for combo in combinations(table, r):
                if sum(self.card_value(c) for c in combo) == target_value:
                    captures.append(list(combo))
        
        return captures
    
    def make_move(self, player, card_index=None):
        """Execute a move for either player or computer"""
        if player == 'player':
            hand = self.player_hand
            collected = self.player_collected
        else:
            hand = self.computer_hand
            collected = self.computer_collected
        
        if player == 'computer':
            # AI selects the best move
            card, capture = self.computer_choose_move()
            if card is None:  # No valid moves, must place a card
                placed_card = random.choice(self.computer_hand)
                self.computer_hand.remove(placed_card)
                self.table_cards.append(placed_card)
                return f"Computer placed {self.format_card(placed_card)}"
        else:
            # Player's turn - card_index comes from GUI
            if card_index is None or card_index >= len(hand):
                return "Invalid move"
            
            card = hand[card_index]
            captures = self.find_valid_captures(card, self.table_cards)
            
            if not captures:  # No captures available, must place card
                hand.remove(card)
                self.table_cards.append(card)
                return f"You placed {self.format_card(card)}"
            
            # For player, we'll use the first valid capture (GUI will let player choose)
            capture = captures[0]
        
        # Execute the capture
        hand.remove(card)
        for c in capture:
            self.table_cards.remove(c)
        collected.extend(capture + [card])
        
        # Check for Chkobba (clearing the table)
        if not self.table_cards:
            collected.append("CHKOBBA!")
            self.last_capturer = player
            return f"{player.capitalize()} captured all cards (CHKOBBA!) with {self.format_card(card)}"
        
        self.last_capturer = player
        return f"{player.capitalize()} captured {len(capture)} cards with {self.format_card(card)}"
    
    def computer_choose_move(self):
        """AI to choose computer's move with some strategy"""
        # First look for captures that include special cards (7♦, etc.)
        for card in self.computer_hand:
            captures = self.find_valid_captures(card, self.table_cards)
            if not captures:
                continue
                
            # Prefer captures that include valuable cards
            for capture in captures:
                for c in capture:
                    if c == (7, '♦'):  # Most valuable card
                        return card, capture
                    if c[1] == '♦':  # Any diamonds
                        return card, capture
                    if c[0] == 7:  # Any sevens
                        return card, capture
            
            # Otherwise take the first available capture
            return card, captures[0]
        
        # No captures available
        return None, None
    
    def is_game_over(self):
        """Check if game has ended"""
        return (not self.deck and 
                not self.player_hand and 
                not self.computer_hand)
    
    def assign_remaining_cards(self):
        """Assign remaining table cards to last capturer"""
        if self.last_capturer == 'player':
            self.player_collected.extend(self.table_cards)
        elif self.last_capturer == 'computer':
            self.computer_collected.extend(self.table_cards)
        self.table_cards = []
    
    def calculate_scores(self):
        """Calculate final scores according to Chkobba rules"""
        p_cards = [c for c in self.player_collected if isinstance(c, tuple)]
        c_cards = [c for c in self.computer_collected if isinstance(c, tuple)]
        
        scores = {"player": 0, "computer": 0}
        
        # 1. Most cards
        if len(p_cards) > len(c_cards):
            scores["player"] += 1
        elif len(c_cards) > len(p_cards):
            scores["computer"] += 1
        
        # 2. Most diamonds (♦)
        p_diamonds = sum(1 for c in p_cards if c[1] == '♦')
        c_diamonds = sum(1 for c in c_cards if c[1] == '♦')
        if p_diamonds > c_diamonds:
            scores["player"] += 1
        elif c_diamonds > p_diamonds:
            scores["computer"] += 1
        
        # 3. 7♦ (most valuable card)
        if (7, '♦') in p_cards:
            scores["player"] += 1
        elif (7, '♦') in c_cards:
            scores["computer"] += 1
        
        # 4. Chkobba bonuses
        scores["player"] += sum(1 for c in self.player_collected if c == "CHKOBBA!")
        scores["computer"] += sum(1 for c in self.computer_collected if c == "CHKOBBA!")
        
        return scores


class ChkobbaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chkobba - Tunisian Card Game")
        self.game = ChkobbaGame()
        
        # Configure styles
        self.bg_color = "#f0f0f0"
        self.card_color = "#ffffff"
        self.btn_color = "#e1e1e1"
        self.font = ("Arial", 12)
        self.card_font = ("Arial", 16, "bold")
        
        self.root.configure(bg=self.bg_color)
        
        # Create GUI elements
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Game info frame
        info_frame = tk.Frame(self.root, bg=self.bg_color)
        info_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            info_frame, 
            text="Welcome to Chkobba! Your turn to play.", 
            font=self.font, 
            bg=self.bg_color
        )
        self.status_label.pack()
        
        # Table frame
        table_frame = tk.LabelFrame(
            self.root, 
            text="Table Cards", 
            padx=10, 
            pady=10, 
            bg=self.bg_color
        )
        table_frame.pack(pady=5)
        self.table_canvas = tk.Canvas(
            table_frame, 
            width=600, 
            height=120, 
            bg="#4a8c3a", 
            highlightthickness=0
        )
        self.table_canvas.pack()
        
        # Player hand frame
        hand_frame = tk.LabelFrame(
            self.root, 
            text="Your Hand", 
            padx=10, 
            pady=10, 
            bg=self.bg_color
        )
        hand_frame.pack(pady=5)
        self.hand_canvas = tk.Canvas(
            hand_frame, 
            width=600, 
            height=120, 
            bg=self.bg_color, 
            highlightthickness=0
        )
        self.hand_canvas.pack()
        
        # Collected cards frame
        collected_frame = tk.Frame(self.root, bg=self.bg_color)
        collected_frame.pack(pady=10)
        
        player_collected_frame = tk.LabelFrame(
            collected_frame, 
            text="Your Collected Cards", 
            padx=5, 
            pady=5, 
            bg=self.bg_color
        )
        player_collected_frame.pack(side=tk.LEFT, padx=5)
        self.player_collected_label = tk.Label(
            player_collected_frame, 
            text="0 cards", 
            font=self.font, 
            bg=self.bg_color
        )
        self.player_collected_label.pack()
        
        computer_collected_frame = tk.LabelFrame(
            collected_frame, 
            text="Computer's Collected Cards", 
            padx=5, 
            pady=5, 
            bg=self.bg_color
        )
        computer_collected_frame.pack(side=tk.LEFT, padx=5)
        self.computer_collected_label = tk.Label(
            computer_collected_frame, 
            text="0 cards", 
            font=self.font, 
            bg=self.bg_color
        )
        self.computer_collected_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(
            button_frame, 
            text="New Game", 
            command=self.new_game, 
            bg=self.btn_color, 
            font=self.font
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.rules_btn = tk.Button(
            button_frame, 
            text="Game Rules", 
            command=self.show_rules, 
            bg=self.btn_color, 
            font=self.font
        )
        self.rules_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind canvas click for card selection
        self.hand_canvas.bind("<Button-1>", self.on_card_click)
    
    def draw_card(self, canvas, card, x, y, face_up=True, tag=None):
        """Draw a card on canvas at specified position"""
        if face_up:
            color = self.card_color
            text = self.game.format_card(card)
            fill = "red" if card[1] in ['♥', '♦'] else "black"
        else:
            color = "#1a66ff"
            text = "🂠"
            fill = "white"
        
        card_id = canvas.create_rectangle(
            x, y, x+70, y+100, 
            fill=color, 
            outline="black", 
            width=2,
            tags=tag
        )
        canvas.create_text(
            x+35, y+50, 
            text=text, 
            font=self.card_font, 
            fill=fill,
            tags=tag
        )
        return card_id
    
    def update_display(self):
        """Update all game displays"""
        # Clear canvases
        self.table_canvas.delete("all")
        self.hand_canvas.delete("all")
        
        # Draw table cards
        for i, card in enumerate(self.game.table_cards):
            self.draw_card(self.table_canvas, card, 20 + i*80, 10)
        
        # Draw player hand
        for i, card in enumerate(self.game.player_hand):
            self.draw_card(self.hand_canvas, card, 20 + i*80, 10, tag=f"card_{i}")
        
        # Update collected cards count
        p_collected = len([c for c in self.game.player_collected if isinstance(c, tuple)])
        c_collected = len([c for c in self.game.computer_collected if isinstance(c, tuple)])
        self.player_collected_label.config(text=f"{p_collected} cards")
        self.computer_collected_label.config(text=f"{c_collected} cards")
        
        # Update status
        if self.game.is_game_over():
            self.game.assign_remaining_cards()
            scores = self.game.calculate_scores()
            winner = "Player" if scores["player"] > scores["computer"] else "Computer" if scores["computer"] > scores["player"] else "Draw"
            self.status_label.config(
                text=f"Game Over! {winner} wins\n" +
                     f"Player: {scores['player']} | Computer: {scores['computer']}"
            )
    
    def on_card_click(self, event):
        """Handle player clicking a card"""
        if self.game.current_player != 'player' or self.game.is_game_over():
            return
        
        # Find which card was clicked
        card_width = 70
        card_index = (event.x - 20) // 80
        
        if 0 <= card_index < len(self.game.player_hand):
            card = self.game.player_hand[card_index]
            captures = self.game.find_valid_captures(card, self.game.table_cards)
            
            if not captures:
                # No captures available, must place card
                result = self.game.make_move('player', card_index)
                self.status_label.config(text=result)
                self.computer_turn()
            else:
                # Let player choose which capture to use (for simplicity, we'll use the first)
                result = self.game.make_move('player', card_index)
                self.status_label.config(text=result)
                self.computer_turn()
            
            self.update_display()
    
    def computer_turn(self):
        """Handle computer's turn"""
        if self.game.is_game_over():
            return
            
        self.game.current_player = 'computer'
        self.root.update()  # Update display before computer moves
        self.root.after(1000, self.execute_computer_move)  # Pause for visibility
    
    def execute_computer_move(self):
        """Execute computer's move after delay"""
        result = self.game.make_move('computer')
        self.status_label.config(text=result)
        self.game.current_player = 'player'
        self.update_display()
        
        # Check if need to deal new cards
        if not self.game.player_hand and not self.game.computer_hand:
            self.game.deal_additional_cards()
            self.update_display()
    
    def new_game(self):
        """Start a new game"""
        self.game.reset_game()
        self.update_display()
        self.status_label.config(text="New game started. Your turn!")
    
    def show_rules(self):
        """Display game rules"""
        rules = """
        Chkobba (Ksob) Card Game Rules:
        
        1. Each player starts with 3 cards, 4 cards on the table
        2. On your turn, play a card to either:
           - Capture cards from the table that:
             * Match your card's value exactly, OR
             * Sum to your card's value
           - Or place your card on the table if no captures available
        3. If you clear the table (CHKOBBA!), you get a bonus point
        4. When all cards are played, the last capturer gets remaining table cards
        5. Scoring:
           - 1 point for most cards collected
           - 1 point for most diamonds (♦) collected
           - 1 point for capturing the 7♦
           - 1 point for each CHKOBBA!
        """
        messagebox.showinfo("Game Rules", rules.strip())


if __name__ == "__main__":
    root = tk.Tk()
    game_gui = ChkobbaGUI(root)
    root.mainloop()
