import multiprocessing as mp

import plane_tracking
import web_api

if __name__ == "__main__":
    update_process = mp.Process(target=plane_tracking.update_loop)
    update_process.start()

    web_api.run_server()
