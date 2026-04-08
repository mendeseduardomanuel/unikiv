using Plataforma_de_Ensino_Online__E_Learning_.Model;

namespace Plataforma_de_Ensino_Online__E_Learning_
{
    internal class Program
    {
        static List<Estudante> estudantes = new List<Estudante>();
        static List<Instrutor> instrutores = new List<Instrutor>();
        static List<Curso> cursos = new List<Curso>();

        static void Main(string[] args)
        {
            bool sair = false;

            while (!sair)
            {
                Console.Clear();
                Console.WriteLine("=== Plataforma E-Learning ===");
                Console.WriteLine("1 - Criar Estudante");
                Console.WriteLine("2 - Criar Instrutor");
                Console.WriteLine("3 - Criar Curso");
                Console.WriteLine("4 - Inscrever Estudante em Curso");
                Console.WriteLine("5 - Listar Cursos e Alunos");
                Console.WriteLine("6 - Avaliar Curso");
                Console.WriteLine("7 - Sair");
                Console.Write("Escolha uma opção: ");

                string opcao = Console.ReadLine();

                switch (opcao)
                {
                    case "1":
                        CriarEstudante();
                        break;
                    case "2":
                        CriarInstrutor();
                        break;
                    case "3":
                        CriarCurso();
                        break;
                    case "4":
                        InscreverEstudante();
                        break;
                    case "5":
                        ListarCursos();
                        break;
                    case "6":
                        AvaliarCurso();
                        break;
                    case "7":
                        sair = true;
                        break;
                    default:
                        Console.WriteLine("Opção inválida!");
                        break;
                }

                if (!sair)
                {
                    Console.WriteLine("Pressione Enter para continuar...");
                    Console.ReadLine();
                }
            }
        }

        static void CriarEstudante()
        {
            Console.Write("Nome do Estudante: ");
            string nome = Console.ReadLine();

            Estudante e = new Estudante
            {
                Id = estudantes.Count + 1,
                Email = $"{nome.Replace(" ", "").ToLower()}@email.com",
                Senha = "1234",
                Progresso = new Dictionary<Curso, double>(),
                Certificados = new List<Certificado>()
            };

            estudantes.Add(e);
            Console.WriteLine($"Estudante '{nome}' criado com sucesso!");
        }

        static void CriarInstrutor()
        {
            Console.Write("Nome do Instrutor: ");
            string nome = Console.ReadLine();

            Instrutor i = new Instrutor
            {
                Id = instrutores.Count + 1,
                Email = $"{nome.Replace(" ", "").ToLower()}@email.com",
                Senha = "1234",
                Bio = "Instrutor",
                Especialidades = new List<string>()
            };

            instrutores.Add(i);
            Console.WriteLine($"Instrutor '{nome}' criado com sucesso!");
        }

        static void CriarCurso()
        {
            Console.Write("Título do Curso: ");
            string titulo = Console.ReadLine();

            Console.WriteLine("Escolha o nível do curso (0-INICIANTE, 1-INTERMEDIO, 2-AVANCADO): ");
            if (!int.TryParse(Console.ReadLine(), out int nivelInt) || nivelInt < 0 || nivelInt > 2)
            {
                Console.WriteLine("Nível inválido!");
                return;
            }

            Curso c = new Curso
            {
                Id = cursos.Count + 1,
                Titulo = titulo,
                Nivel = (NivelCurso)nivelInt
            };

            cursos.Add(c);
            Console.WriteLine($"Curso '{titulo}' criado com sucesso!");
        }

        static void InscreverEstudante()
        {
            if (estudantes.Count == 0 || cursos.Count == 0)
            {
                Console.WriteLine("Crie pelo menos um estudante e um curso antes de inscrever.");
                return;
            }

            Console.WriteLine("Escolha o estudante:");
            for (int i = 0; i < estudantes.Count; i++)
                Console.WriteLine($"{i + 1} - {estudantes[i].GetPerfil()}");

            if (!int.TryParse(Console.ReadLine(), out int estIndex) || estIndex < 1 || estIndex > estudantes.Count)
            {
                Console.WriteLine("Estudante inválido!");
                return;
            }

            Console.WriteLine("Escolha o curso:");
            for (int i = 0; i < cursos.Count; i++)
                Console.WriteLine($"{i + 1} - {cursos[i].Titulo}");

            if (!int.TryParse(Console.ReadLine(), out int curIndex) || curIndex < 1 || curIndex > cursos.Count)
            {
                Console.WriteLine("Curso inválido!");
                return;
            }

            Estudante e = estudantes[estIndex - 1];
            Curso c = cursos[curIndex - 1];

            e.Progresso[c] = 0.0; // inscreve com nota inicial 0
            Console.WriteLine($"Estudante inscrito no curso '{c.Titulo}' com sucesso!");
        }

        static void ListarCursos()
        {
            foreach (var c in cursos)
            {
                Console.WriteLine($"Curso: {c.Titulo} | Nível: {c.Nivel}");
                Console.WriteLine("Alunos inscritos:");

                var alunos = estudantes.Where(e => e.Progresso.ContainsKey(c)).ToList();
                if (alunos.Count == 0)
                    Console.WriteLine("Nenhum aluno inscrito.");
                else
                    foreach (var a in alunos)
                        Console.WriteLine($"- {a.GetPerfil()}");

                Console.WriteLine("---------------------------");
            }
        }

        static void AvaliarCurso()
        {
            if (cursos.Count == 0)
            {
                Console.WriteLine("Nenhum curso disponível.");
                return;
            }

            Console.WriteLine("Escolha o curso para avaliar:");
            for (int i = 0; i < cursos.Count; i++)
                Console.WriteLine($"{i + 1} - {cursos[i].Titulo}");

            if (!int.TryParse(Console.ReadLine(), out int index) || index < 1 || index > cursos.Count)
            {
                Console.WriteLine("Curso inválido!");
                return;
            }

            Curso c = cursos[index - 1];

            Console.Write("Digite a nota (0-10): ");
            if (!double.TryParse(Console.ReadLine(), out double nota) || nota < 0 || nota > 10)
            {
                Console.WriteLine("Nota inválida!");
                return;
            }

            c.Avaliar(nota);
            Console.WriteLine($"Curso '{c.Titulo}' avaliado com nota {nota}.");
        }
    }
}
