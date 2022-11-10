# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: fgomes-s <fgomes-s@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/11/08 11:17:22 by fgomes-s          #+#    #+#              #
#    Updated: 2022/11/10 15:36:46 by fgomes-s         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

SRCS = ft_atoi.c ft_bzero.c ft_calloc.c ft_isalnum.c ft_isalpha.c ft_isascii.c \
       ft_isdigit.c ft_isprint.c ft_memchr.c ft_memcmp.c ft_memcpy.c ft_memmove.c \
	   ft_memset.c ft_strchr.c ft_strdup.c ft_strcat.c ft_strcpy.c ft_strlen.c ft_strncmp.c\
	   ft_strnstr.c ft_strrchr.c ft_substr.c ft_tolower.c ft_toupper.c ft_strjoin.c\
	
OBJS = $(SRCS:.c=.o)

BONUS =	 
BONUS_OBJS = $(BONUS:.c=.o)

CC = gcc
RM = rm -rf
CFLAGS = -Werror -Wextra -Wall 

NAME = libft.a

all: $(NAME)

$(NAME): $(OBJS)
	@ar -rcs $(NAME) $(OBJS)

$(OBJS): $(SRCS)
	@$(CC) $(CFLAGS) -c $(SRCS)

clean:
	@$(RM) $(OBJS) $(BONUS_OBJS)

fclean:	clean
	@$(RM) $(NAME)

re:	fclean all

bonus: $(OBJS) $(BONUS_OBJS)
	@ar -rcs $(NAME) $(OBJS) $(BONUS_OBJS)