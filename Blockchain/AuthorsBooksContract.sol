// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts@5.0.1/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@5.0.1/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts@5.0.1/token/ERC721/extensions/ERC721Pausable.sol";
import "@openzeppelin/contracts@5.0.1/access/Ownable.sol";
import "@openzeppelin/contracts@5.0.1/token/ERC721/extensions/ERC721Burnable.sol";
//import {PaymentSplitter} from "@openzeppelin/contracts/finance/PaymentSplitter.sol";
//adiconado para fazer o split do pagamento


/// @custom:security-contact alexfett@gmail.com
contract BOOKS_AUTHOR is ERC721, ERC721Enumerable, ERC721Pausable, Ownable, ERC721Burnable  {
    uint256 private _nextTokenId;
    //uint256 private _daysRental;
    //uint256 private _rentalPrice; //integer divided by 100

    //mapping com a data de expiracao do token
    mapping(uint256 => uint256) public expirationDate;

    string public baseURI;
    string private baseExtension = ".json";

    constructor(address initialOwner, string memory bookISBN,string memory bookToken)
        ERC721(bookISBN, bookToken)
        Ownable(initialOwner)
    {}

    //function getDaysRental() public view returns string

    //function expirationDate( expDateRental)
    //function bookISBN()
    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }

    function safeMint(address to) public onlyOwner {
        uint256 tokenId = _nextTokenId++;
        //O token expira após 60 dias
        expirationDate[tokenId] = block.timestamp + 60 days;
        
        _safeMint(to, tokenId);
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return baseURI;
    }

    function setBaseUri(string memory _baseUri) public onlyOwner {
        baseURI = _baseUri;
    }

    
    // sobre escreve as funçoes para verificar se o token ta expirado antes de transferir
    //https://docs.openzeppelin.com/contracts/2.x/api/token/erc721#ERC721-_exists-uint256-
//    function _beforeTokenTransfer( address from, address to, uint256 tokenId)
//        internal  
//        override(ERC721, ERC721Pausable)
//    {
         
//        require(expirationDate[tokenId] > block.timestamp, "Err: token transfer BLOQUEADA, NFT esta expirado");   
//        super._beforeTokenTransfer(from, to, tokenId);
//    }

//    function tokenIdExists(uint256 tokenId)
//        external 
//        returns (bool)
//    {
        
//        return super._exists(tokenId);
//    }

    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable, ERC721Pausable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
 // https://medium.com/@juanxaviervalverde/erc721enumerable-extension-what-how-and-why-8ba3532ea195
}
