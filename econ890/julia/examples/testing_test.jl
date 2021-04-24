# Testing `Testing`

using Test

include("testing.jl");
using .Testing

function test_function(x)
    @testset "test_function $x" begin
        oneX = one(eltype(x));
        # This passes
        @test plus_one(x) == x + oneX
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