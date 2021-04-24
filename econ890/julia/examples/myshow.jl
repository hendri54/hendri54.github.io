# Packaged into a module for easy reloading (with Revise) 
# and to avoid polluting the global namespace.
# This illustrates multiple dispatch with a fallback method.
module MyShow

## --------  The "matlab" implementation
# It is tempting to do this, but not efficient and not extendable.

function myshow_bad(x :: T) where T
    if T <: Integer
        println("$T $x");
    elseif T <: AbstractFloat
        println("$T $(round(x, digits = 1))");
    else
        println("I do not know this type: $T");
    end
    return nothing
end

## ----------  The Julian way, using multiple dispatch
# Note that we can add new methods for other types.

myshow(x :: T) where T <: Integer = println("$T $x");

myshow(x :: T) where T <: AbstractFloat = println("$T $(round(x, digits = 1))");

# Fallback method
myshow(x :: T) where T = println("I do not know this type: $T");


myshow(1);
myshow(1.2345);
myshow("any other type");

end