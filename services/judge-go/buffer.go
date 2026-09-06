package main

import "bytes"

// capBuffer — chegaralangan bufer. Chegaradan oshsa yozishni to'xtatadi va
// bayroq qo'yadi: bu 08-ole case'idagi OLE verdictining manbai.
type capBuffer struct {
	buf     bytes.Buffer
	limit   int64
	written int64
	// onExceed chegaraga yetganda BIR MARTA chaqiriladi — jarayonni
	// darhol to'xtatish uchun. Busiz cheksiz chiqish beruvchi dastur
	// wall chegarasigacha ishlab, judge vaqtini yeydi: o'lchovda
	// 2007 ms vs isolate ning 14 ms i (143x).
	onExceed func()
	fired    bool

	Exceeded bool
}

func (c *capBuffer) Write(p []byte) (int, error) {
	if c.limit > 0 && c.written+int64(len(p)) > c.limit {
		room := c.limit - c.written
		if room > 0 {
			c.buf.Write(p[:room])
			c.written += room
		}
		c.Exceeded = true
		if !c.fired && c.onExceed != nil {
			c.fired = true
			c.onExceed()
		}
		return len(p), nil // yozganday ko'rsatamiz — jarayon SIGPIPE olmasin
	}
	n, err := c.buf.Write(p)
	c.written += int64(n)
	return n, err
}

func (c *capBuffer) String() string { return c.buf.String() }
