# COS473 Final Project: Zk-Swap: Implementing Uniswap on zkEVM Polygon to Harness Speed, Lower Transaction Fees, and Utilize Less Gas

The protocol in this part is derived from [Uniswap v2](https://docs.uniswap.org/protocol/V2/introduction), where we use [constant product formula x * y = k](https://docs.uniswap.org/protocol/V2/concepts/protocol-overview/how-uniswap-works) to determine exchange prices. A formal specification of the constant product market maker model can be found [here](https://github.com/runtimeverification/verified-smart-contracts/blob/uniswap/uniswap/x-y-k.pdf).

## Swap interface
Basic functions of DEXs in `contracts/Swap.sol` to manage a liquidity pool made up of reserves of two sAsset tokens and enable exchanges between them. Please follow the below specifications and the interfaces defined in `contracts/interfaces/ISwap.sol`. 

### State variables

* `token0` / `token1`: addresses of a pair of sAsset tokens
* `reserve0` / `reserve1`: quantity of each sAsset token in the pool
* `totalShares`: the total amount of shares owned by all liquidity providers
* `shares`: a mapping from the address of a liquidity provider to the number of shares owned by the liquidity provider. `shares[LP] / totalShares` represents the relative proportion of total reserves that each liquidity provider has contributed

### Functions
There are some functions already implemented for the initial setup.

* `init` is used by the first liquidity provider (in our project it should be the owner of the contract) to deposit both tokens with equal values. The ratio of tokens defines the initial exchange rate and reflects the price of two tokens in the global market as the liquidity provider believes. The amount of initial shares follows [Uniswap v2 (section 3.4)](https://uniswap.org/whitepaper.pdf) and is set to be equal to the geometric mean of the amounts deposited: `shares = sqrt(amount0 * amount1)`.
* `sqrt` is a helper function to calculate square root.
* `getReserves` is a view function that returns the reserves of two tokens.
* `getTokens` is a view function that returns the addresses of two tokens.
* `getShares` is a view function that returns the number of shares owned by the given address.
* `addLiquidity` is used by future liquidity providers to deposit tokens, and will generate new shares based on the token amount in the deposit w.r.t. the pool. Adding liquidity requires an equivalent value of two tokens. Callers need to specify the amount of token 0 they want to deposit (`amount0`) and the amount of token 1 required to be added (`amount1`) is determined using the reserve rate at the moment of their deposit, i.e.,`amount1 = reserve1 * amount0 / reserve0`. And the amount of shares received by the liquidity provider is: `new_shares = total_shares * amount0 / reserve0`.
* `token0To1` / `token1To0` are the functions for converting token 0/1 to token 1/0 while maintaining the relationship `reserve0 * reserve1 = invariant`. The input specifies the number of source tokens sent to the smart contract, the function then computes the number of target tokens sent to the caller based on the current price rate and the input (after subtracting the 0.3% protocol fee). 
