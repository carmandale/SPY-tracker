CREATE TABLE daily_predictions (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	"preMarket" FLOAT, 
	"predLow" FLOAT, 
	"predHigh" FLOAT, 
	bias VARCHAR, 
	"volCtx" VARCHAR, 
	"dayType" VARCHAR, 
	"keyLevels" VARCHAR, 
	notes VARCHAR, 
	open FLOAT, 
	noon FLOAT, 
	"twoPM" FLOAT, 
	close FLOAT, 
	"realizedLow" FLOAT, 
	"realizedHigh" FLOAT, 
	"rangeHit" BOOLEAN, 
	"absErrorToClose" FLOAT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME, source TEXT, locked INTEGER DEFAULT 0, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_daily_predictions_id ON daily_predictions (id);
CREATE UNIQUE INDEX ix_daily_predictions_date ON daily_predictions (date);
CREATE TABLE price_logs (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	checkpoint VARCHAR NOT NULL, 
	price FLOAT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_price_logs_date ON price_logs (date);
CREATE INDEX ix_price_logs_checkpoint ON price_logs (checkpoint);
CREATE INDEX ix_price_logs_id ON price_logs (id);
CREATE TABLE ai_predictions (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	checkpoint VARCHAR NOT NULL, 
	predicted_price FLOAT NOT NULL, 
	confidence FLOAT NOT NULL, 
	reasoning VARCHAR, 
	market_context VARCHAR, 
	actual_price FLOAT, 
	prediction_error FLOAT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_ai_predictions_id ON ai_predictions (id);
CREATE INDEX ix_ai_predictions_checkpoint ON ai_predictions (checkpoint);
CREATE INDEX ix_ai_predictions_date ON ai_predictions (date);
CREATE UNIQUE INDEX idx_ai_predictions_date_checkpoint 
ON ai_predictions(date, checkpoint);
