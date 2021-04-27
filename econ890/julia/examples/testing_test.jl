# Testing `Testing`

# Needed so we can use `@test`
using Test

# We somehow need to get the code to be tested to be visible.
# Usually, we are testing packages. Then just `using Testing`.
include("testing.jl");
# Note the period (because `Testing` is not a package, it is a sub-module of `Main`)
using .Testing

# We can (should!) wrap tests in functions, like all other code.
# This is a good way of testing a common interface: run the same tests and all types
# that are expected to support the interface.
function test_function(x)
    # Then we need a `@testset inside the function`
    @testset "test_function $x" begin
        oneX = one(eltype(x));
        # This passes
        @test plus_one(x) == x + oneX
        # This passes
        @test plus_one(x) isa typeof(oneX)
        # Testing broadcasting (passes)
        @test plus_one.([x, x]) == x .+ fill(oneX, 2)
    end
end

@testset "Testing All" begin
    # This test passes
    @test plus_one(1) == 2
    # This one fails
    @test plus_one(1) == 1
    # Tests packaged inside a function
    test_function(2.0)
    # Nested testset
    @testset "Nested" begin
        @test plus_one(3) == 4
        @test plus_one(3) == 3
    end
end

# -----------