#!/bin/env python3

"""
MIT License

Copyright (c) 2021 Andrey Sakhar <a@sakhar.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def read_commands(filename):
  operations = {}
  with open(filename, 'r') as file:
    lines = file.readlines()
    for line in lines:
      row = line.split('\t')
      bits = ''.join(row[2].split(' | ')).replace(' ', '')
      operations[bits] = row[1]
    # print(row)
  return operations
# print(operations)

def tobinary(byte):
  binary = bin(int(byte, 16))[2:]
  return '0'*(8-len(binary))+binary

def disassemble(filename, operations):
  datas = ''
  with open(filename, 'r') as file:
    lines = file.readlines()
    for line in lines:
      size = int(line[1:3], 16)
      offset = int(line[3:7], 16)
      typ = int(line[7:9], 16)
      data = line[9:9+(size<<1)]
      chksum = line[-2:]
      check = sum(map(lambda x: int(x, 16), (line[i:i+2] for i in range(1, len(line)-1, 2))))%256
      if check != 0:
        print(f"; ERROR: Check sum failed! ({check})")
        exit(1)
      print(f"; {size=}, {offset=}, {typ=}, data='{data}', chksum=0x{chksum}")
      if typ==0:
        if len(datas)>>3 < offset:
          datas += '0'*((offset<<3)-len(datas))
        datas += ''.join(list(map(tobinary, (data[i<<1:(i<<1)+2] for i in range(len(data)>>1)))))
  datas = ''.join(datas[i+8:i+16]+datas[i:i+8] for i in range(0, len(datas), 16))
  print("\n\n; DISASSEMBLY:\n")
  i = 0
  while i < len(datas):
    opcode = None
    for opcode, opname in operations.items():
      args = {}
      resi = i
      for bit in opcode:
        if i == len(datas):
          i = resi
          break
        if (bit == '0' or bit == '1'):
          if bit==datas[i]:
            i += 1
            continue
          i = resi
          break
        if not (bit in args):
          args[bit] = ''
        args[bit] += datas[i]
        i += 1
      if i == resi:
        continue
      if(opname == 'NOP'):
        print(f"address_{hex(resi>>4)}:")
      name_args_req = opname.split(' ', 1)
      if len(name_args_req) == 1:
        print(opname)
        break
      name = name_args_req[0]
      args_req = name_args_req[1].split(', ')
      print(name, end='\t')
      outargs = []
      for ar in args_req:
        if ar[0] == 'R':
          nums = args[ar[1]]
          if len(args[ar[1]]) != 5:
            nums = '1'+nums
          outargs.append(f'R{int(nums, 2)}')
        if ar[0] == 'K':
          outargs.append(f'{int(args["K"], 2)} ; (=0b{args["K"]})')
        if ar[0] == 'k':
          outargs.append(f'{hex(int(args["k"], 2))} ; (=0b{args["k"]})')
        if ar[0] == 'P':
          outargs.append(f'{hex(int(args["P"], 2))}')
        if ar[0] == 'Y':
          outargs.append('Y')
        if ar[0] == 'Z':
          outargs.append('Z')
        if ar[0] == 'D':
          wregs = {'10':'Y','11':'X','00':'Z'}
          outargs.append(f"{wregs[args['D']]}")
        if ar[0] == 'X':
          if not ('X' in args):
            outargs.append('X')
          else:
            outargs.append(f'{args["X"]} ; (X threated as wildcard)')
      print(',\t'.join(outargs))
      break
    if i == resi:
      sys.stderr.write(f"Cannot disassemble bytes: '{datas[i:i+32]}'\n")
      raise Exception("No match")


def print_err(file):
  import traceback
  nl = '\n'
  sys.stderr.write(f"Error: Failed to disassemble {file}!\n\t{traceback.format_exc().split(nl)[-2]}\n")

if __name__ == "__main__":
  import sys
  stdout = sys.stdout
  import argparse
  parser = argparse.ArgumentParser(description='Get source code for intel hex files.')
  parser.add_argument('files', metavar='FILES', type=open, nargs='+',
                      help='hex files')
  parser.add_argument('--intructions', dest="instr", nargs="?", help='provide the file containing instructions table')
  parser.add_argument('-s', '--silent', dest='silent', help="Suppress output (not errors)", action="store_true")
  parser.add_argument('-xs', '--totalsilent', dest='totalsilent', help="Suppress output and errors", action="store_true")
  args = parser.parse_args()
  
  instfile = './commands.txt'
  if args.instr:
    instfile = args.instr

  operations = read_commands(instfile)

  for filewrapper in args.files:
    file = filewrapper.name
    filewrapper.close()
    try:
      with open(file[::-1].replace('xeh.', '', 1)[::-1]+".asm", 'w') as f:
        sys.stdout = f
        try:
          disassemble(file, operations)
        except Exception as e:
          if not args.totalsilent:
            print_err(file)
          continue
    except (PermissionError, FileNotFoundError) as e:
      if not args.totalsilent:
        print_err(file)
      continue
    if not args.silent and not args.totalsilent:
      stdout.write(f"Disassembled {file} to {file.replace('.hex', '.asm')}\n")