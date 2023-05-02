FROM node:18.2.0-bullseye-slim

WORKDIR /app

COPY ./app/package.json ./

RUN npm install

COPY ./app .

EXPOSE 3000

CMD npm run dev
# RUN npm install --silent
# RUN npm install react-scripts@5.0.1 -g --silent
# RUN npm install react-router-dom
# RUN npm install react-markdown
# RUN npm install --save sweetalert2 @sweetalert2/theme-dark

# RUN npm uninstall eslint --save-dev
# # Copiar la aplicación
# COPY ./my-app ./

# # Ejecutar la aplicación
# CMD ["npm", "start"]