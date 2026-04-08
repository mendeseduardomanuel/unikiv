using System;
using System.Collections.Generic;
using System.Text;

namespace Sistema_de_Gestao_de_Veiculos.Model
{
    public abstract class Veiculo : IManutencao
    {
        public string Matricula { get; set; }
        public string Marca { get; set; }
        public string Modelo { get; set; }
        public int Ano { get; set; }
        public double Km { get; set; }
        public EstadoVeiculo Estado { get; set; } = EstadoVeiculo.DISPONIVEL;

        protected List<Manutencao> manutencoes = new List<Manutencao>();

        public void AdicionarKm(double km) => Km += km;
        public abstract string GetTipo();
        public virtual double CalcularValorDiaria() => 100;

        public void Agendar(DateTime data) { /* simplificado */ }
        public void RealizarManutencao() { /* simplificado */ }
        public List<Manutencao> ObterHistorico() => manutencoes;
    }
}
