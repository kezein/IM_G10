SELECT * FROM profriends_inc.buyer;

ALTER TABLE household
ADD CONSTRAINT fk_household_buyer
FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID);

ALTER TABLE loan
ADD CONSTRAINT fk_loan_buyer
FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID);

ALTER TABLE employment
ADD CONSTRAINT fk_employment_buyer
FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID);

ALTER TABLE spouse
ADD CONSTRAINT fk_spouse_buyer
FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID);

ALTER TABLE beneficiary
ADD CONSTRAINT fk_beneficiary_buyer
FOREIGN KEY (BuyerID) REFERENCES buyer(BuyerID);