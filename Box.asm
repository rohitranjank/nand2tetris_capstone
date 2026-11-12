// Box.asm  --  K = 13
// Box: starts at row 13, 20 rows tall, 32 pixels wide (2 words) from left edge.
// Start address = SCREEN + 32*13 = 16384 + 416 = 16800
// Black while any key is pressed, white when released.

(LOOP)
    // choose colour: color = (KBD != 0) ? -1 : 0
    @KBD
    D=M
    @BLACK
    D;JNE
    @color
    M=0
    @START
    0;JMP
(BLACK)
    @color
    M=-1

(START)
    @20
    D=A
    @n              // n = rows left to draw
    M=D
    @16800
    D=A
    @addr           // addr = first word of current row
    M=D

(ROW)
    @color
    D=M
    @addr
    A=M
    M=D             // word 0 of the row (pixels 0-15)
    A=A+1
    M=D             // word 1 of the row (pixels 16-31)

    @32
    D=A
    @addr
    M=D+M           // move down one screen row (+32 words)

    @n
    M=M-1
    D=M
    @ROW
    D;JGT           // repeat until 20 rows are done

    @LOOP
    0;JMP
