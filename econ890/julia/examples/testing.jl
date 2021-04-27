module Testing
# Module to illustrate testing basics.

export plus_one

# Why not just `x + 1` or `x + 1.0`?
plus_one(x :: T) where T <: Number = x + one(T);

end