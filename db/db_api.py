import json
from .models import (Filial,
                    Review,
                    Source,
                    create_db,
                    session,
                    engine,
                    TABLES)
from .models.tg_models import (User,
                              Status,
                              user_status,
                              Request,
                              requests_view)
from sqlalchemy.orm import Session
from sqlalchemy import inspect, update
from sqlalchemy import and_

def _add_base_info():
    with open('meta/base_statuses.json', 'r') as f:
        statuses = json.loads(f.read())
        for st in statuses:
            Status.add(name=st['name'],
                       description=st['description'])

def create_user_status_trigger(Session : Session = session()):
    trigger = """
    CREATE FUNCTION check_active_user_status()
	RETURNS trigger
	AS 
	$func$
	BEGIN
		IF (SELECT 1 FROM user_status AS us WHERE us.user_id = NEW.user_id AND us.status_id = NEW.status_id AND us.is_active = TRUE AND us.is_active = NEW.is_active) THEN 
			RAISE EXCEPTION 'This status on this user already exist and active, deactivate previous status';
		END IF;
		RETURN NEW;
	END;
	$func$ LANGUAGE plpgsql;
    CREATE TRIGGER user_status_INSERT 
    	BEFORE INSERT ON user_status
    	FOR EACH ROW EXECUTE FUNCTION check_active_user_status();
     
    CREATE FUNCTION check_active_requests()
	RETURNS trigger
	AS 
	$func$
	BEGIN
		IF (SELECT 1 FROM requests AS r WHERE r.user_id = NEW.user_id AND r.status_id = NEW.status_id AND r.is_active = TRUE) THEN 
			RAISE EXCEPTION 'This request already exist and active.';
		END IF;
		RETURN NEW;
	END;
	$func$ LANGUAGE plpgsql;
    CREATE TRIGGER request_INSERT 
    	BEFORE INSERT ON requests
    	FOR EACH ROW EXECUTE FUNCTION check_active_requests();
    """
    Session.execute(trigger)
    Session.commit()
    Session.close()
def create_database_if_not_exist():
    if not inspect(engine).has_table(TABLES[0]):
        create_db()
        create_user_status_trigger()
        _add_base_info()
        

if __name__ == "__main__":
    create_database_if_not_exist()
    
    
    
    