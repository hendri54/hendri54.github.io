module Test1

abstract type AbstractUtility{T} end
abstract type AbstractProdFct{T} end

struct CRRA{T} <: AbstractUtility{T}
    σ :: T
end

struct CobbDouglas{T} <: AbstractProdFct{T}
    α :: T
end

# Note the `T` in the parametric type definition
struct Model{T, U <: AbstractUtility{T}, F <: AbstractProdFct{T}}
    util :: U
    prodFct :: F
end

m = Model(CRRA(2.0), CobbDouglas(0.3))
@show m

try
    m2 = Model(CRRA(Float32(2)), CobbDouglas(0.3))
    @show m2
catch
    println("This errors because the parametric types don't match.");
end

end