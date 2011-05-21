# game of life

alive = (c == 1) &  ((m_cnt == 2) | (m_cnt == 3))
born  = (m_cnt == 3) & (c == 0)
c   = alive | born


# parity

c = e ^ w ^ s ^ n ^ c

# squares

c = where(m_cnt > 0, 1,0)

# diamonds

c = n | s | e | c | s | w


# 1 out of 8

c = (m_cnt == 1) | c 

# lichens

c = (m_cnt == 3) | (m_cnt == 7) | (m_cnt == 8) | c

# lichens with death

alive = (m_cnt == 3) | (m_cnt == 7) | (m_cnt == 8) | c
dead = m_cnt == 4
c = (alive & ~dead)

# majority

c = where(m_total > 4, 1, 0)

# anneal

c = ((m_total > 5) | (m_total == 4)) & ~((m_total == 5) | (m_total < 4))


# banks

sum = n + s + e + w
c = where(sum > 2, 1,c)
c = where((sum == 2) & (n != s),0,c)

###### second order dynamics #####

# brian's brain

c[1:7] = 0          # hide the bits we're not using
save = c[7] & on[0] # save the old value of c[7] 
c[7] = (m_cnt[7] == 2) & (c[7] == 0) & (c[0] == 0)
c[0] = save
# the save = c[7] & on[0] includes the '& on[0]' because of the
# way Numeric works. by default Numeric will make new arrays just references
# to old arrays. using '& on[0]' doesn't have any effect on the logic
# but it forces Numeric to make a whole new array for 'save' rather than just
# pointing to the old one.

# greenberg

c[1:7] = 0
save = c[7] & on[0]
t = n[7] | s[7] | e[7] | c[7] | w[7]
c[7] = t & (c[0] == 0) & (c[7] == 0)
c[0] = save


# parity-flip
c[1:7] = 0
save = c[7] & on[0]
c[7] = c[7] ^ n[7] ^ s[7] ^ w[7] ^ e[7] ^ c[0]
c[0] = save

# time-tunnel
c[1:7] = 0
save = c[7] & on[0]
sum = c[7] + n[7] + s[7] + w[7] + e[7]
t = (sum == 0) | (sum == 5)
c[7] = t ^ c[0]
c[0] = save

# genetic drift
c[1:7] = 0
save = c[7] & on[0]
sum = (2 * c[7]) + c[0]
c[7] = ((sum == 0) & n[7]) | ((sum == 1) & s[7]) | ((sum == 2) & w[7]) | ((sum == 3) & e[7])
c[6] = ((sum == 0) & n[0]) | ((sum == 1) & s[0]) | ((sum == 2) & w[0]) | ((sum == 3) & e[0])
