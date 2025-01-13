from app import db

class Database(db.Model):
    __tablename__ = 'databases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    time_series = db.relationship('TimeSeriesData', backref='database', lazy=True)

class TimeSeriesData(db.Model):
    __tablename__ = 'time_series_data'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    database_id = db.Column(db.Integer, db.ForeignKey('databases.id'), nullable=False)

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'value': self.value
        }
