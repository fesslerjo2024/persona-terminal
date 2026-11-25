"""Native terminal artwork for the monorail and Champs de Fleurs routes."""
from persona3_environment_reels import monorail
from persona3_scenic_detail import hotel_hall


def train(w,h,car,t=0.,*,braking=False,stopped=False):
    return monorail(w,h,car,t,braking=braking,stopped=stopped)


def hotel(w,h,floor,room_count,focus):
    return hotel_hall(w,h,floor,room_count,focus)
