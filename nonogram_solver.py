import numpy as np
import copy
import time
import os
from subprocess import call

# I wrote most of this code almost a year ago,
# Now I completely hate it, all the pointless classes,
# inconsistant indentation, and bad names.
#
# TODO (Maybe): Refactor

do_animation = False
animation_pause_secs = 0.05

def split(n, size):
  res = []
  if size > 1:
    for i in range(n + 1):
      t = split(i, size - 1)
      for j in t:
        if isinstance(j, int):
          res.append([n - i, j])
        else:
          j.insert(0, n - i)
          res.append(j)
    return res
  else:
    return [n]

class Clue:
  def __init__(self, _nums, _size):
    self.nums = [int(i) for i in _nums]
    self.size = _size
    self.possibilities = []

  def getPossible(self):
    freeSpace = self.size - sum(self.nums) - len(self.nums) + 1
    sections = []
    #create sections
    for i, val in enumerate(self.nums):
      t = [2] * val
      if i < (len(self.nums) - 1):
        t.append(1)
      sections.append(t)
    #generate all possible separations
    seps = split(freeSpace, len(self.nums) + 1)
    #generate all possible solutions
    res = []
    for i in seps:
      t = []
      for j in range(len(i) - 1):
        t.extend([1] * i[j])
        t.extend(sections[j])
      t.extend([1] * i[-1])
      res.append(t)
    self.possibilities = np.array(res)

def overlap(clue, state: np.array):
  res = None
  # find all possibilities that satisfy the state and throw out the rest
  xonly = state.copy()
  fonly = state.copy()
  xonly[xonly == 0] = 1
  fonly[fonly == 0] = 2
  remove = np.empty([len(clue.possibilities)], bool)
  for index, i in enumerate(clue.possibilities):
    b = not False in (i == xonly) | (i == fonly)
    remove[index] = b
    if b: # if i satisfies the condition
      if res is None:
        res = i.copy()
      else:
         # find overlaps between remaining values
        res *= np.equal(res, i)
        #for j in range(len(res)):
        #  if res[j] != i[j]:
        #    res[j] = 0    
  clue.possibilities = clue.possibilities[remove]
  return res
 
class GameBoard:
  def __init__(self, size, clues, check_unique):
      self.boardState = np.zeros(size, dtype = int)
      self.lastBoardState = np.ones(size, dtype = int)
      self.clues = clues
      self.check_unique = check_unique
      self.recursion_required = False

  def getClueRowFromInt(self, n):
      # rows first, then columns
      if n < self.boardState.shape[0]:
        return self.clues[n], self.boardState[n]
      else:
        return self.clues[n], self.boardState[:, n - self.boardState.shape[0]]

  def setRowFromInt(self, n, val):
      if n < self.boardState.shape[0]:
        self.boardState[n] = val
      else:
        self.boardState[:, n - self.boardState.shape[0]] = val

  def getProbabitities(self):
    rows_prob_mat = np.zeros(self.boardState.shape)
    cols_prob_mat = np.zeros(self.boardState.shape)
    for i in range(self.boardState.shape[0]):
      # assuming the board is in a possible state
      p_sum = sum(np.array(self.clues[i].possibilities) == 2) / len(self.clues[i].possibilities)
      rows_prob_mat[i] = p_sum
    for i in range(self.boardState.shape[1]):
      p_sum = sum(np.array(self.clues[i + self.boardState.shape[0]].possibilities) == 2) / len(self.clues[i + self.boardState.shape[0]].possibilities)
      cols_prob_mat[:, i] = p_sum
    product = rows_prob_mat * cols_prob_mat
    return (product - 0.5)# * np.logical_and(product != 0, product != 1)

  def attemptSolve(self):
    self.animateFrame()
    for c in self.clues:
      c.getPossible()
    rowsOfInterest = np.ones((self.boardState.shape[0] + self.boardState.shape[1]))
    while rowsOfInterest.any() == 1:
      tmp = rowsOfInterest.copy()
      rowsOfInterest = np.zeros_like(tmp)
      for i in range(len(tmp)):
        if tmp[i] == 1:
          c, r = self.getClueRowFromInt(i)
          r1 = overlap(c, r)
          if r1 is None:
            return False # This configuration is not solvable
          diff = r - r1
          if i < self.boardState.shape[0]:
            for j in range(len(diff)):
              if diff[j] != 0:
                rowsOfInterest[j + self.boardState.shape[0]] = 1
          else:
            for j in range(len(diff)):
              if diff[j] != 0:
                rowsOfInterest[j] = 1
          self.setRowFromInt(i, r1)
          self.animateFrame()

    if 0 in self.boardState:
      if not self.recursion_required and not do_animation:
        print("Recursion was required to solve this puzzle")
        self.recursion_required = True
      prob = self.getProbabitities()
      max_index = np.unravel_index(np.argmin(np.abs(prob)), self.boardState.shape)
      best_guess = (prob[max_index] > 0) + 1
      board_copy_a = copy.deepcopy(self)
      board_copy_b = copy.deepcopy(self)
      board_copy_a.boardState[max_index] = best_guess
      first_guess_correct = False
      if (board_copy_a.attemptSolve()):
        self.boardState = board_copy_a.boardState
        self.clues = board_copy_a.clues
        self.check_unique = board_copy_a.check_unique
        if not self.check_unique:
            return True
        first_guess_correct = True

      board_copy_b.boardState[max_index] = (best_guess % 2) + 1
      state_solvable = board_copy_b.attemptSolve()
      if state_solvable:
        if first_guess_correct and False:
          print("Multiple solutions detected")
          #board_copy_b.printBoard()
          #self.check_unique = 0
        else:  
          self.boardState = board_copy_b.boardState
          self.clues = board_copy_b.clues
          self.check_unique = board_copy_b.check_unique
        return True
      else:
        return first_guess_correct
    print("")
    self.printBoard()
    return True

  def printBoard(self):
    for row in self.boardState:
      current_row_string = ""
      for i in row:
        if i == 0:
          current_row_string += '? '
        elif i == 1:
          current_row_string += "X "
        else:
          current_row_string += "█ "
      print(current_row_string)

  def animateFrame(self):
    if do_animation and not np.equal(self.boardState, self.lastBoardState).all():
      # reset the cursor to 0, 0
      print("\033[0;0H")
      self.printBoard()
      print()
      self.lastBoardState = self.boardState.copy()
      time.sleep(animation_pause_secs)

def clueListFromStr(string, size):
  string = string.replace(' ', '')
  clueStrings = string.split(';')
  res = []
  for i in range(size[0]):
    t = clueStrings[i].split(',')
    res.append(Clue(t, size[1]))
  res.reverse()
  for i in range(size[0], size[0] + size[1]):
    t = clueStrings[i].split(',')
    res.append(Clue(t, size[0]))
  return res

if __name__ == "__main__":
    size = (0, 0)
    while size == (0, 0):
      size_str = input("What size puzzle are you solving? (H x W): ").lower().replace(' ', '')
      try:
        size = (int(size_str), int(size_str))
      except:
        delims = 'x*'
        for d in delims:
          if d in size_str:
            split_sizes = size_str.split(d)
            try:
              size = (int(split_sizes[0]), int(split_sizes[1]))
            except:
              print("Not a valid size.")
              size = (0, 0)
              continue
            if len(split_sizes) != 2:
              print("Only 2d puzzles are supported")
              size = (0, 0)
              continue
            else:
              break
        if size == (0, 0):
          print("Not a valid size.")
          continue

    print("Enter the clues, one line at a time, reading clockwise. If there is more than one number, use a comma. type b to go back");
    clue_str = ""
    i = 0
    while i < (size[0] + size[1]):
      clue_input = input(str(i) + ':').replace(' ', '').replace(';', '')
      if (clue_input.lower() == "back" or clue_input.lower() == "b"):
        i -= 1
        clue_str = clue_str[0 : clue_str.rfind(';', 0, max(clue_str.rfind(';'), 0)) + 1]
        continue
      clue_str += clue_input + ';'
      i += 1

    print()
    clues = clueListFromStr(clue_str, size)
    board = GameBoard(size, clues, 1)
    if (do_animation):
      _ = call('clear' if os.name =='posix' else 'cls')
    if not board.attemptSolve():
      print("This board is not solvable!")
      exit(1)
    #if (do_animation):
    #  _ = call('clear' if os.name =='posix' else 'cls')
    #if not do_animation:
    #    print()
    #    board.printBoard()
    print()
